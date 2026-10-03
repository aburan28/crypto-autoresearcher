import os, shutil, sys, re

DESTINATION_PATH = os.path.dirname( __file__ ) + '/release_mupq'
MQOM3_C_SOURCE_CODE_FOLDER = os.path.dirname( __file__ ) + '/../../mqom3_ref'

MQOM3_C_SOURCE_CODE_SUBFOLDERS = ['ggm_tree', 'blc', 'fields', 'fields_bitsliced', 'piop', 'rijndael']
MQOM3_C_SOURCE_CODE_FILES = [
    'api.h',
    'common.h',
    'domain_separation.h',
    'benchmark.h',
    'enc.h',
    'enc_local.h',
    'enc_mupq.h',
    'enc_liboqs.h',
    'expand_mq.c',
    'expand_mq.h',
    'fields.h',
    'ggm_tree/ggm_tree_common.h',
    'ggm_tree/ggm_tree_common_ecb.h',
    'ggm_tree/ggm_tree_large_common_impl.c',
    'ggm_tree/ggm_tree_large_dfs.c',
    'ggm_tree/ggm_tree_large_dfs.h',
    'ggm_tree/ggm_tree_large.h',
    'ggm_tree/ggm_tree_large_common.h',
    'ggm_tree/ggm_tree_large_bfs.c',
    'ggm_tree/ggm_tree_large_bfs.h',
    'ggm_tree/ggm_tree_large_incr.c',
    'ggm_tree/ggm_tree_large_incr.h',
    'ggm_tree/ggm_tree_large_incr_batch.c',
    'ggm_tree/ggm_tree_large_incr_batch.h',
    'ggm_tree/ggm_tree_small.c',
    'ggm_tree/ggm_tree_small.h',
    'ggm_tree/ggm_tree_small_incr.h',
    'ggm_tree/ggm_tree_small_incr_batch.c',
    'ggm_tree/ggm_tree_small_incr_batch.h',
    'ggm_tree/ggm_tree_small_incr.c',
    'keygen.c',
    'keygen.h',
    'mqom3_parameters.h',
    'prg.h',
    'seed_expand.h',
    'prg.c',
    'seed_expand.c',
    'seed_expand_cache.h',
    'seed_expand_impl.h',
    'seed_expand_xn_impl.h',
    'sign.c',
    'sign_memopt.c',
    'sign.h',
    'sign_pre.c',
    'sign_pre.h',
    'verify_stream.h',
    'verify_stream_ct.c',
    'verify_stream_ct.h',
    'verify_stream_ot.c',
    'verify_stream_ot.h',
    'sample_challenge_common.h',
    'sample_challenge_sign.h',
    'sample_challenge_verify.h',
    'crypto_sign.c',
    'xof.c',
    'xof.h',
    'blc/blc.h',
    'blc/blc_common.h',
    'blc/blc_convert.h',
    'blc/blc_ct.h',
    'blc/blc_ot.h',
    'blc/blc_ct_common.h',
    'blc/blc_ct_default.c',
    'blc/blc_ct_default.h',
    'blc/blc_ot_default.c',
    'blc/blc_ot_default.h',
    'blc/blc_ct_memopt.c',
    'blc/blc_ct_memopt.h',
    'blc/blc_ot_memopt.c',
    'blc/blc_ot_memopt.h',
    'blc/blc_memopt.h',
    'blc/blc_memopt_folding.h',
    'blc/blc_memopt_seedcommit.h',
    'blc/seed_commit.h',
    'blc/seed_commit_default.h',
    'blc/seed_commit_impl.h',
    'blc/seed_commit_memopt.h',
    'blc/seed_commit_memopt_impl.h',
    'fields/fields_arm_neon.h',
    'fields/fields_avx2.h',
    'fields/fields_avx512.h',
    'fields/fields_common.h',
    'fields/fields_handling.h',
    'fields/fields_ref.h',
    'fields/gf256_mult_table.h',
    'fields_bitsliced.h',
    'fields_bitsliced/fields_bitsliced_branchconst_composite.h',
    'fields_bitsliced/fields_bitsliced_branchconst.h',
    'piop/piop_cache.h',
    'piop/piop_common.h',
    'piop/piop_default.c',
    'piop/piop_default.h',
    'piop/piop_memopt.c',
    'piop/piop_memopt.h',
    'piop/piop_bitslice.c',
    'piop/piop_bitslice.h',
    'piop/piop.h',
    'rijndael/rijndael_aes_ni.c',
    'rijndael/rijndael_aes_ni.h',
    'rijndael/rijndael_vaes.c',
    'rijndael/rijndael_vaes.h',
    'rijndael/rijndael_common.h',
    'rijndael/rijndael_ct64_enc.h',
    'rijndael/rijndael_ct64.c',
    'rijndael/rijndael_ct64.h',
    'rijndael/rijndael_platform.h',
    'rijndael/rijndael_ref.c',
    'rijndael/rijndael_ref.h',
    'rijndael/rijndael_table.c',
    'rijndael/rijndael_table.h',
    'rijndael/rijndael_external.c',
    'rijndael/rijndael_external.h',
    'rijndael/rijndael.h',
    'rijndael/rijndael_arm_aes.c',
    'rijndael/rijndael_arm_aes.h',
    'LICENSE',
]

def copy_folder(src_path, dst_path, only_root=False):
    for root, dirs, files in os.walk(src_path):
        subpath = root[len(src_path)+1:]
        root_created = False
        for filename in files:
            _, file_extension = os.path.splitext(filename)
            if file_extension in ['.h', '.c' ] or filename in ['LICENSE']:
                if not root_created:
                    os.makedirs(os.path.join(dst_path, subpath))
                    root_created = True
                shutil.copyfile(
                    os.path.join(src_path, subpath, filename),
                    os.path.join(dst_path, subpath, filename)
                )


shutil.rmtree(DESTINATION_PATH, ignore_errors=True)
os.makedirs(DESTINATION_PATH)

TARGET_TMPL = "mqom3_cat{}_{}_{}_{}"
LEVELS = [1, 3, 5]
# Valid (field_exp, tradeoff) combinations for round 3: gf16 has fast/short, gf2 has shorter only
FIELD_TRADEOFFS = [(4, "fast"), (4, "short"), (1, "shorter")]
VARIANTS = ["ct", "ot"]

# Per-profile compile-time options, transcribed from mqom-embedded's
# tools/reproduce_variant.py (_CT_/_OT_ x FAST/SHORT x BAL/MEM) - the script that
# actually produced the Cortex-M4 figures. Keyed on (BLC variant, tradeoff,
# profile) and NOT on the tradeoff alone: the profiles genuinely differ between
# Correlated Trees and One big Tree. The CT sets tune the small-tree knobs
# (SMALL_GGM_TREE_*, BLC_SEEDCOMMIT_CACHE, BLC_SEEDEXPAND_CACHE) while the OT
# sets tune the large tree (LARGE_GGM_TREE_INCR_BATCH, BLC_NO_FAST_FOLDING with
# BLC_NB_LEAF_SEEDS_IN_PARALLEL 2). Indexing on the tradeoff alone, as this
# script did, handed the nine OT instances the CT settings.
#
# "shorter" reuses the "short" sets, exactly as reproduce_variant.py aliases
# _CT_SHORTER_* to _CT_SHORT_*.
#
# Board-only knobs are deliberately left out, since none of them is meaningful
# in a pqm4 tree: RIJNDAEL_OPT_ARMV7M (the ARMv7-M assembly is not part of this
# export, and pqm4 supplies AES-128 itself through MQOM3_FOR_MUPQ),
# RIJNDAEL_TABLE / RIJNDAEL_EXTERNAL / USE_GF256_TABLE_LOG_EXP (LUT profile
# only, which this export does not carry), RIJNDAEL_TABLE_FORCE_IN_FLASH
# (linker sections, and NO_EMBEDDED_SRAM_SECTION below leaves them to pqm4) and
# BLC_OT_BATCH_SIZE (a per-run knob, not a profile: these instances are the
# default single traversal).
PROFILE_FLAGS = {
    ('ct', 'fast', 'balanced'): [
        'PIOP_BITSLICE',
        'FIELDS_BITSLICE_COMPOSITE',
        'FIELDS_BITSLICE_PUBLIC_JUMP',
        'MEMORY_EFFICIENT_BLC',
        'MEMORY_EFFICIENT_KEYGEN',
        'GGMTREE_NB_ENC_CTX_IN_MEMORY 0',
        'SMALL_GGM_TREE_NB_SIMULTANEOUS_LEAVES_LOG 5',
        'BLC_NB_LEAF_SEEDS_IN_PARALLEL 32',
        'BLC_SEEDCOMMIT_CACHE',
        'BLC_SEEDEXPAND_CACHE',
    ],
    ('ct', 'short', 'balanced'): [
        'PIOP_BITSLICE',
        'FIELDS_BITSLICE_COMPOSITE',
        'FIELDS_BITSLICE_PUBLIC_JUMP',
        'MEMORY_EFFICIENT_BLC',
        'MEMORY_EFFICIENT_KEYGEN',
        'SMALL_GGM_TREE_NB_SIMULTANEOUS_LEAVES_LOG 7',
        'BLC_NB_LEAF_SEEDS_IN_PARALLEL 64',
        'BLC_SEEDCOMMIT_CACHE',
        'BLC_SEEDEXPAND_CACHE',
    ],
    ('ot', 'fast', 'balanced'): [
        'PIOP_BITSLICE',
        'FIELDS_BITSLICE_COMPOSITE',
        'FIELDS_BITSLICE_PUBLIC_JUMP',
        'MEMORY_EFFICIENT_BLC',
        'MEMORY_EFFICIENT_KEYGEN',
        'BLC_NB_LEAF_SEEDS_IN_PARALLEL 32',
        # Value flag, not a bare toggle: the Makefile emits
        # -DLARGE_GGM_TREE_INCR_BATCH=$(...) and the header rejects anything
        # that is not 0 or 1, so a valueless #define breaks the build.
        'LARGE_GGM_TREE_INCR_BATCH 1',
    ],
    ('ot', 'short', 'balanced'): [
        'PIOP_BITSLICE',
        'FIELDS_BITSLICE_COMPOSITE',
        'FIELDS_BITSLICE_PUBLIC_JUMP',
        'MEMORY_EFFICIENT_BLC',
        'MEMORY_EFFICIENT_KEYGEN',
        'BLC_NB_LEAF_SEEDS_IN_PARALLEL 32',
        # Value flag, not a bare toggle: the Makefile emits
        # -DLARGE_GGM_TREE_INCR_BATCH=$(...) and the header rejects anything
        # that is not 0 or 1, so a valueless #define breaks the build.
        'LARGE_GGM_TREE_INCR_BATCH 1',
    ],
    ('ct', 'fast', 'memopt'): [
        'MEMORY_EFFICIENT_PIOP',
        'FIELDS_BITSLICE_COMPOSITE',
        'FIELDS_BITSLICE_PUBLIC_JUMP',
        'MEMORY_EFFICIENT_BLC',
        'MEMORY_EFFICIENT_KEYGEN',
        'GGMTREE_NB_ENC_CTX_IN_MEMORY 0',
        'SIGN_MEMOPT',
        'VERIFY_MEMOPT',
        'PRG_ONE_RIJNDAEL_CTX',
        'SEED_COMMIT_MEMOPT',
        'PIOP_NB_PARALLEL_REPETITIONS_SIGN 9',
        'PIOP_NB_PARALLEL_REPETITIONS_VERIFY 4',
        'SMALL_GGM_TREE_NB_SIMULTANEOUS_LEAVES_LOG 4',
        'BLC_NB_LEAF_SEEDS_IN_PARALLEL 8',
    ],
    ('ct', 'short', 'memopt'): [
        'MEMORY_EFFICIENT_PIOP',
        'FIELDS_BITSLICE_COMPOSITE',
        'FIELDS_BITSLICE_PUBLIC_JUMP',
        'MEMORY_EFFICIENT_BLC',
        'MEMORY_EFFICIENT_KEYGEN',
        'GGMTREE_NB_ENC_CTX_IN_MEMORY 0',
        'SIGN_MEMOPT',
        'VERIFY_MEMOPT',
        'PRG_ONE_RIJNDAEL_CTX',
        'SEED_COMMIT_MEMOPT',
        'PIOP_NB_PARALLEL_REPETITIONS_SIGN 9',
        'PIOP_NB_PARALLEL_REPETITIONS_VERIFY 4',
        'SMALL_GGM_TREE_NB_SIMULTANEOUS_LEAVES_LOG 4',
        'BLC_NB_LEAF_SEEDS_IN_PARALLEL 8',
    ],
    ('ot', 'fast', 'memopt'): [
        'MEMORY_EFFICIENT_PIOP',
        'FIELDS_BITSLICE_COMPOSITE',
        'FIELDS_BITSLICE_PUBLIC_JUMP',
        'MEMORY_EFFICIENT_BLC',
        'MEMORY_EFFICIENT_KEYGEN',
        'SIGN_MEMOPT',
        'VERIFY_MEMOPT',
        'PRG_ONE_RIJNDAEL_CTX',
        'SEED_COMMIT_MEMOPT',
        'PIOP_NB_PARALLEL_REPETITIONS_SIGN 9',
        'PIOP_NB_PARALLEL_REPETITIONS_VERIFY 4',
        'BLC_NO_FAST_FOLDING',
        'BLC_NB_LEAF_SEEDS_IN_PARALLEL 2',
        'GGMTREE_NB_ENC_CTX_IN_MEMORY 0',
    ],
    ('ot', 'short', 'memopt'): [
        'MEMORY_EFFICIENT_PIOP',
        'FIELDS_BITSLICE_COMPOSITE',
        'FIELDS_BITSLICE_PUBLIC_JUMP',
        'MEMORY_EFFICIENT_BLC',
        'MEMORY_EFFICIENT_KEYGEN',
        'SIGN_MEMOPT',
        'VERIFY_MEMOPT',
        'PRG_ONE_RIJNDAEL_CTX',
        'SEED_COMMIT_MEMOPT',
        'PIOP_NB_PARALLEL_REPETITIONS_SIGN 9',
        'PIOP_NB_PARALLEL_REPETITIONS_VERIFY 4',
        'BLC_NO_FAST_FOLDING',
        'BLC_NB_LEAF_SEEDS_IN_PARALLEL 2',
        'GGMTREE_NB_ENC_CTX_IN_MEMORY 0',
    ],
    # "Reference" implementation, mostly here for "host" side tests of MUPQ.
    # It has no counterpart in reproduce_variant.py, hence the same set for
    # every variant and tradeoff.
    ('ct', 'fast', 'ref'): [
        'MEMORY_EFFICIENT_BLC',
        'MEMORY_EFFICIENT_PIOP',
        'FIELDS_BITSLICE_PUBLIC_JUMP',
        'MEMORY_EFFICIENT_KEYGEN',
    ],
}
for _v in VARIANTS:
    for _t in ('fast', 'short'):
        PROFILE_FLAGS[(_v, _t, 'ref')] = PROFILE_FLAGS[('ct', 'fast', 'ref')]

for l in LEVELS:
    for (field, trade_off) in FIELD_TRADEOFFS:
        for variant in VARIANTS:
            for impl in ['balanced', 'memopt', 'ref']:
                    instance_path = os.path.join(
                        DESTINATION_PATH, 'crypto_sign',
                        TARGET_TMPL.format(l, f'gf{2**field}', trade_off, variant), impl
                    )
                    shutil.rmtree(instance_path, ignore_errors=True)
                    os.makedirs(instance_path)
                    for filename in MQOM3_C_SOURCE_CODE_FILES:
                        if l == 1 and field == 4 and trade_off == "fast" and variant == "ct":
                            shutil.copyfile(
                                os.path.join(MQOM3_C_SOURCE_CODE_FOLDER, filename),
                                os.path.join(instance_path, os.path.split(filename)[1])
                            )
                        else:
                            # Create symlinks for common files
                            base_path = os.path.join(
                                '../../',
                                TARGET_TMPL.format(1, f'gf16', "fast", "ct"), impl
                            )
                            os.symlink(os.path.join(base_path, os.path.split(filename)[1]), os.path.join(instance_path, os.path.split(filename)[1]))
    
                    shutil.copyfile(
                        os.path.join(MQOM3_C_SOURCE_CODE_FOLDER, 'parameters', f'mqom3_parameters_cat{l}_gf{2**field}_{trade_off}_{variant}.h'),
                        os.path.join(instance_path, f'mqom3_parameters_cat{l}_gf{2**field}_{trade_off}_{variant}.h')
                    )
    
                    # Generate "parameters.h" with the proper parameters
                    parameters = "#ifndef __PARAMETERS_H__\n#define __PARAMETERS_H__\n\n"
                    if l == 1:
                        parameters += "#define MQOM3_PARAM_SECURITY 128\n"
                    elif l == 3:
                        parameters += "#define MQOM3_PARAM_SECURITY 192\n"
                    else:                    
                        parameters += "#define MQOM3_PARAM_SECURITY 256\n"
                    #
                    parameters += ("#define MQOM3_PARAM_BASE_FIELD %d\n" % field)
                    #
                    if trade_off == "fast":
                        parameters += "#define MQOM3_PARAM_TRADEOFF 0\n"
                    elif trade_off == "short":
                        parameters += "#define MQOM3_PARAM_TRADEOFF 1\n"
                    else:
                        parameters += "#define MQOM3_PARAM_TRADEOFF 2\n"
                    #
                    if variant == "ct":
                        parameters += "#define MQOM3_PARAM_OT_VARIANT 0\n\n"
                    else:
                        parameters += "#define MQOM3_PARAM_OT_VARIANT 1\n\n"
                    #
                    parameters += "/* Fields conf: ref implementation */\n#define FIELDS_REF\n"
                    parameters += "/* Rijndael conf: bitslice (actually underlying MUPQ implementation for cat1 with the MQOM3_FOR_MUPQ toggle) */\n#define RIJNDAEL_BITSLICE\n"
                    # Opt specific to the implementation. "shorter" shares the
                    # "short" profiles, as reproduce_variant.py does.
                    profile_key = (variant, "fast" if trade_off == "fast" else "short", impl)
                    if profile_key not in PROFILE_FLAGS:
                        print("Error: unknown implementation type %s" % impl)
                        sys.exit(-1)
                    parameters += "/* Options activated for memory optimization */\n"
                    for flag in PROFILE_FLAGS[profile_key]:
                        parameters += "#define %s\n" % flag
                    parameters += "/* Specifically target MUPQ */\n#define MQOM3_FOR_MUPQ\n\n/* Do not mess with sections as the PQM4 framework uses them */\n"
                    parameters += "#define NO_EMBEDDED_SRAM_SECTION\n\n#endif /* __PARAMETERS_H__ */\n"
                    with open(os.path.join(instance_path, 'parameters.h'), 'w') as f:
                        f.write(parameters)
    
                    if l == 1 and field == 4 and trade_off == "fast" and variant == "ct":
                        # Patch the generic parameters to include "parameters.h"
                        with open(os.path.join(instance_path, f'mqom3_parameters.h'), 'r') as f:
                            content = f.read()
                        content = content.replace("#define __MQOM3_PARAMETERS_GENERIC_H__\n", "#define __MQOM3_PARAMETERS_GENERIC_H__\n\n#include \"parameters.h\"\n")
                        content = content.replace("\"parameters/mqom3", "\"mqom3")
                        with open(os.path.join(instance_path, f'mqom3_parameters.h'), 'w') as f:
                            f.write(content)

# Now we must replace some stuff: all the #include with a subfolder.
# Every instance directory is flat - the copy above keeps only the basename -
# so a "blc/blc_ct_memopt.h" or "../ggm_tree/ggm_tree_large.h" include, which
# resolves fine in the source tree thanks to the Makefile -I flags, resolves to
# nothing here. Without this pass, sign_pre.c and verify_stream_{ct,ot}.c fail
# to compile in every instance.
include_regex = re.compile(r'#include\s*[<"]([^">]+/[^\s">]+)[">]')

def process_file_for_header(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    def replacement(match):
        full_path = match.group(1)  # e.g., sha3/aa.h or foo/bar/baz.h
        filename = os.path.basename(full_path)  # e.g., aa.h or baz.h
        return f'#include "{filename}"'
    new_content = include_regex.sub(replacement, content)
    if new_content != content:
        print(f"Modified header for: {filepath}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

def replace_all_headers(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith((".c", ".h")):
                path = os.path.join(root, filename)
                if not os.path.islink(path):  # skip symlinks
                    process_file_for_header(path)

replace_all_headers(DESTINATION_PATH)
