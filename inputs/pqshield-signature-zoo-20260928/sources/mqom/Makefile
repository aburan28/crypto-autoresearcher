# Compiler detection
# Detect if we are using clang or gcc
CLANG :=  $(shell $(CC) -v 2>&1 | grep clang)
ifeq ($(CLANG),)
  GCC :=  $(shell $(CC) -v 2>&1 | grep gcc)
endif

ifneq ($(CLANG),)
  # get clang version e.g. 14.1.3
  CLANG_VERSION := $(shell $(CROSS_COMPILE)$(CC) -dumpversion)
  # convert to single number e.g. 14 * 100 + 1
  CLANG_VERSION := $(shell echo $(CLANG_VERSION) | cut -f1-2 -d. | sed -e 's/\./*100+/g')
  # Calculate value - e.g. 1401
  CLANG_VERSION := $(shell echo $$(($(CLANG_VERSION))))
  # Comparison results (true if true, empty if false)
  CLANG_VERSION_GTE_12 := $(shell [ $(CLANG_VERSION) -ge 1200 ]  && echo true)
  CLANG_VERSION_GTE_13 := $(shell [ $(CLANG_VERSION) -ge 1300 ]  && echo true)
  CLANG_VERSION_GTE_16 := $(shell [ $(CLANG_VERSION) -ge 1600 ]  && echo true)
  CLANG_VERSION_GTE_17 := $(shell [ $(CLANG_VERSION) -ge 1700 ]  && echo true)
  CLANG_VERSION_GTE_18 := $(shell [ $(CLANG_VERSION) -ge 1800 ]  && echo true)
  CLANG_VERSION_GTE_19 := $(shell [ $(CLANG_VERSION) -ge 1900 ]  && echo true)
endif

# AR and RANLIB
AR ?= ar
RANLIB ?= ranlib

# Probe -march=native / -mcpu=native / -mtune=native individually before adding them
# to the default CFLAGS: some compilers/targets (e.g. arm-none-eabi-gcc used for
# embedded cross-builds) reject one or more of these flags outright ("unrecognized
# -mcpu target: native"), which would otherwise hard-fail every compile. Skipped
# entirely when NO_NATIVE_TUNE=1 is already requested. NO_NATIVE_TUNE=1 remains the
# manual escape hatch for a flag that compiles but mistunes for the real target.
ifneq ($(NO_NATIVE_TUNE),1)
  CC_SUPPORTS_MARCH_NATIVE := $(shell $(CC) -march=native -E -x c /dev/null -o /dev/null 2>/dev/null && echo 1)
  CC_SUPPORTS_MCPU_NATIVE  := $(shell $(CC) -mcpu=native -E -x c /dev/null -o /dev/null 2>/dev/null && echo 1)
  CC_SUPPORTS_MTUNE_NATIVE := $(shell $(CC) -mtune=native -E -x c /dev/null -o /dev/null 2>/dev/null && echo 1)
  ifeq ($(CC_SUPPORTS_MARCH_NATIVE),1)
    NATIVE_TUNE_FLAGS += -march=native
  endif
  ifeq ($(CC_SUPPORTS_MCPU_NATIVE),1)
    NATIVE_TUNE_FLAGS += -mcpu=native
  endif
  ifeq ($(CC_SUPPORTS_MTUNE_NATIVE),1)
    NATIVE_TUNE_FLAGS += -mtune=native
  endif
endif

# Basic CFLAGS
CFLAGS ?= -O3 $(NATIVE_TUNE_FLAGS) -Wall -Wextra -Wshadow -DNDEBUG
# Dependency tracking flags: kept separate from CFLAGS so that the $(shell ...)
# platform-detection commands (which read from stdin via -E -) do not generate
# spurious "-.d" files when they expand $(CFLAGS).
DEPFLAGS = -MMD -MP

# Keccak related stuff, in the form of an external library
LIB_HASH_DIR = sha3
LIB_HASH = $(LIB_HASH_DIR)/libhash.a

# Rinjdael related stuff
RIJNDAEL_DIR = rijndael
RIJNDAEL_INCLUDES = $(RIJNDAEL_DIR)
RIJNDAEL_SRC_FILES = $(RIJNDAEL_DIR)/rijndael_ref.c $(RIJNDAEL_DIR)/rijndael_table.c $(RIJNDAEL_DIR)/rijndael_aes_ni.c $(RIJNDAEL_DIR)/rijndael_vaes.c $(RIJNDAEL_DIR)/rijndael_ct64.c $(RIJNDAEL_DIR)/rijndael_external.c $(RIJNDAEL_DIR)/rijndael_arm_aes.c
ifeq ($(RIJNDAEL_OPT_ARMV7M),1)
  # Force RIJNDAEL optimized assembly usage where possible
  CFLAGS += -DRIJNDAEL_OPT_ARMV7M
  ASMFLAGS += -x assembler-with-cpp
  RIJNDAEL_SRC_FILES += $(RIJNDAEL_DIR)/aes128_table_arvmv7m.s $(RIJNDAEL_DIR)/aes128_fixsliced_arvmv7m.s
endif
RIJNDAEL_OBJS   = $(patsubst %.c,%.o, $(filter %.c,$(RIJNDAEL_SRC_FILES)))
RIJNDAEL_OBJS  += $(patsubst %.s,%.o, $(filter %.s,$(RIJNDAEL_SRC_FILES)))
RIJNDAEL_OBJS  += $(patsubst %.S,%.o, $(filter %.S,$(RIJNDAEL_SRC_FILES)))

# GGMTree related stuff
GGM_DIR = ggm_tree
GGM_INCLUDES = $(GGM_DIR)
GGM_SRC_FILES = $(GGM_DIR)/ggm_tree_small.c $(GGM_DIR)/ggm_tree_small_incr.c $(GGM_DIR)/ggm_tree_small_incr_batch.c
# The large-tree units are OT-only and say so themselves (MQOM3_VARIANT_GUARD).
GGM_SRC_FILES += $(GGM_DIR)/ggm_tree_large_common_impl.c $(GGM_DIR)/ggm_tree_large_dfs.c $(GGM_DIR)/ggm_tree_large_incr.c
GGM_SRC_FILES += $(GGM_DIR)/ggm_tree_large_incr_batch.c
GGM_SRC_FILES += $(GGM_DIR)/ggm_tree_large_bfs.c
GGM_OBJS   = $(patsubst %.c,%.o, $(filter %.c,$(GGM_SRC_FILES)))
GGM_OBJS  += $(patsubst %.s,%.o, $(filter %.s,$(GGM_SRC_FILES)))
GGM_OBJS  += $(patsubst %.S,%.o, $(filter %.S,$(GGM_SRC_FILES)))

# BLC related stuff
BLC_DIR = blc
BLC_INCLUDES = $(BLC_DIR)
# Both families are compiled; each is guarded (MQOM3_VARIANT_GUARD).
BLC_SRC_FILES = $(BLC_DIR)/blc_ot_default.c $(BLC_DIR)/blc_ot_memopt.c
BLC_SRC_FILES += $(BLC_DIR)/blc_ct_default.c $(BLC_DIR)/blc_ct_memopt.c
BLC_OBJS   = $(patsubst %.c,%.o, $(filter %.c,$(BLC_SRC_FILES)))
BLC_OBJS  += $(patsubst %.s,%.o, $(filter %.s,$(BLC_SRC_FILES)))
BLC_OBJS  += $(patsubst %.S,%.o, $(filter %.S,$(BLC_SRC_FILES)))

# PIOP related stuff
PIOP_DIR = piop
PIOP_INCLUDES = $(PIOP_DIR)
PIOP_SRC_FILES = $(PIOP_DIR)/piop_default.c $(PIOP_DIR)/piop_memopt.c $(PIOP_DIR)/piop_bitslice.c
PIOP_OBJS   = $(patsubst %.c,%.o, $(filter %.c,$(PIOP_SRC_FILES)))
PIOP_OBJS  += $(patsubst %.s,%.o, $(filter %.s,$(PIOP_SRC_FILES)))
PIOP_OBJS  += $(patsubst %.S,%.o, $(filter %.S,$(PIOP_SRC_FILES)))

# Fields related stuff
# TODO
FIELDS_DIR = fields
FIELDS_BITSLICE_DIR = fields_bitsliced
FIELDS_INCLUDES = $(FIELDS_DIR) $(FIELDS_BITSLICE_DIR)

# MQOM3 related elements
MQOM3_DIR = .
MQOM3_INCLUDES = $(MQOM3_DIR)
MQOM3_SRC_FILES = $(MQOM3_DIR)/xof.c $(MQOM3_DIR)/prg.c $(MQOM3_DIR)/seed_expand.c $(MQOM3_DIR)/expand_mq.c $(MQOM3_DIR)/keygen.c $(MQOM3_DIR)/sign.c $(MQOM3_DIR)/sign_memopt.c $(MQOM3_DIR)/sign_pre.c $(MQOM3_DIR)/crypto_sign.c
# StreamedVerify (Init/Update/Finalize/Clean): CT/OT split only, like BLC_SRC_FILES;
# it calls the memopt BLC/PIOP primitives by their explicit names (see verify_stream.h),
# so it needs no memopt-related flag to be compiled in.
MQOM3_SRC_FILES += $(MQOM3_DIR)/verify_stream_ot.c $(MQOM3_DIR)/verify_stream_ct.c
MQOM3_OBJS   = $(patsubst %.c,%.o, $(filter %.c,$(MQOM3_SRC_FILES)))
MQOM3_OBJS  += $(patsubst %.s,%.o, $(filter %.s,$(MQOM3_SRC_FILES)))
MQOM3_OBJS  += $(patsubst %.S,%.o, $(filter %.S,$(MQOM3_SRC_FILES)))

# Extra source files possibly provided by the user
EXTRA_OBJS  =$(patsubst %.c,%.o, $(filter %.c,$(EXTRA_SRC)))
EXTRA_OBJS +=$(patsubst %.s,%.o, $(filter %.s,$(EXTRA_SRC)))
EXTRA_OBJS +=$(patsubst %.S,%.o, $(filter %.S,$(EXTRA_SRC)))

OBJS = $(RIJNDAEL_OBJS) $(GGM_OBJS) $(BLC_OBJS) $(PIOP_OBJS) $(MQOM3_OBJS) $(EXTRA_OBJS)

ifneq ($(GCC),)
  # Remove gcc's -Warray-bounds and -W-stringop-overflow/-W-stringop-overread as they give many false positives
  CFLAGS += -Wno-array-bounds -Wno-stringop-overflow -Wno-stringop-overread
endif

######## Compilation toggles
## Adjust the optimization targets depending on the platform
ifeq ($(RIJNDAEL_TABLE),1)
  # Table based optimized *non-constant time* Rijndael
  CFLAGS += -DRIJNDAEL_TABLE
endif
ifeq ($(RIJNDAEL_AES_NI),1)
  # AES-NI (requires support on the x86 platform) constant time Rijndael
  CFLAGS += -DRIJNDAEL_AES_NI
endif
ifeq ($(RIJNDAEL_VAES),1)
  # VAES (Vector AES): separate implementation; opt-in only, AES-NI is the default on VAES-capable CPUs
  CFLAGS += -DRIJNDAEL_VAES
endif
ifeq ($(NO_RIJNDAEL_VAES_GFNI_KEYSCHED),1)
  # Force-disable the GFNI-accelerated AES-128 x2/x4/x8 key schedule
  # (VGF2P8AFFINEINVQB) even when the compiler target provides GFNI; it is
  # otherwise auto-detected in rijndael_platform.h, like RIJNDAEL_VAES256_VBMI.
  CFLAGS += -DNO_RIJNDAEL_VAES_GFNI_KEYSCHED
endif
ifeq ($(RIJNDAEL_CONSTANT_TIME_REF),1)
  # Reference constant time (slow) Rijndael
  CFLAGS += -DRIJNDAEL_CONSTANT_TIME_REF
endif
ifeq ($(RIJNDAEL_BITSLICE),1)
  # Constant time bitslice Rijndael
  CFLAGS += -DRIJNDAEL_BITSLICE
endif
ifeq ($(RIJNDAEL_CT64_CT_KEYSCHED),1)
  # Force constant time key schedule for the bitsliced ct64 variant
  CFLAGS += -DRIJNDAEL_CT64_CT_KEYSCHED
endif
ifeq ($(RIJNDAEL_TABLE_FORCE_IN_FLASH),1)
  # Force the tables for "rijndael table based" to be in flash
  CFLAGS += -DRIJNDAEL_TABLE_FORCE_IN_FLASH
endif
# External Rijndael:
ifeq ($(RIJNDAEL_EXTERNAL),1)
  # Externally provided Rijndael
  CFLAGS += -DRIJNDAEL_EXTERNAL
endif
# Public (non-secret) Rijndael backend selection. By default the public path uses
# the table implementation regardless of the private backend, because it only ever
# processes public data and tables are fast. Setting RIJNDAEL_PRIV_PUB_COMMON=1
# makes it use the same implementation as the private one instead - uniform, and
# constant time when the private backend is. The knob existed in rijndael.h but
# nothing could define it.
ifeq ($(RIJNDAEL_PRIV_PUB_COMMON),1)
  CFLAGS += -DRIJNDAEL_PRIV_PUB_COMMON
endif
# Opt out of in-place encryption (in == out) for any backend whose aliasing
# behaviour is unknown. Covers the block, xN and ECB primitives alike: every
# in-tree backend reads its whole input group before writing, but third-party
# ones (RIJNDAEL_EXTERNAL, liboqs, mupq) are bound by no such contract.
ifeq ($(RIJNDAEL_NO_INPUTS_ALIASING),1)
  CFLAGS += -DRIJNDAEL_NO_INPUTS_ALIASING
endif
ifeq ($(RIJNDAEL_ARM_AES),1)
  # ARM Crypto Extension hardware AES (AArch64 / ARMv7 with Crypto Extension)
  CFLAGS += -DRIJNDAEL_ARM_AES
endif

## For fields, we detect if we are on a 64 bit __x86_64__: if this is not the case (32 bits)
## our implementation does not support it (because some intrinsics specifically use 64 bits registers)
DETECT_PLATFORM_X64=$(shell $(CC) $(CFLAGS) $(EXTRA_CFLAGS) -dM -E - < /dev/null 2> /dev/null |egrep __x86_64__)
DETECT_PLATFORM_NEON=$(shell $(CC) $(CFLAGS) $(EXTRA_CFLAGS) -dM -E - < /dev/null 2> /dev/null |egrep '__ARM_NEON__|__ARM_NEON')
# Big endian ARM: NEON is auto-detected there too (the target does define
# __ARM_NEON), but the NEON backend is little endian only - it mixes the byte
# view and the uint16_t view of the same register. Detect it so the cascade
# below falls back to FIELDS_REF instead, exactly as fields.h does.
DETECT_PLATFORM_ARM_BE=$(shell $(CC) $(CFLAGS) $(EXTRA_CFLAGS) -dM -E - < /dev/null 2> /dev/null |egrep '__ARM_BIG_ENDIAN|__AARCH64EB__|__ARMEB__')
ifeq ($(DETECT_PLATFORM_X64),)
  # On non-x86 platforms, check for ARM NEON before falling back to fields ref.
  # The test covers all four backends, not just REF/NEON: with only those two,
  # an explicit FIELDS_AVX2=1 or FIELDS_AVX512=1 on a non-x86 target used to get
  # FIELDS_REF added on top of it, and fields.h then silently resolved the pair
  # in favour of REF. It is now either honoured (and fails on the intrinsics,
  # which is the honest answer) or rejected by the exclusivity guard in fields.h.
  ifeq ($(FIELDS_REF)$(FIELDS_NEON)$(FIELDS_AVX2)$(FIELDS_AVX512),)
    ifneq ($(DETECT_PLATFORM_NEON),)
      ifeq ($(DETECT_PLATFORM_ARM_BE),)
        FIELDS_NEON = 1
      else
        FIELDS_REF = 1
      endif
    else
      FIELDS_REF = 1
    endif
  endif
endif
#
ifeq ($(FIELDS_REF),1)
  # Reference implementation for fields
  CFLAGS += -DFIELDS_REF
endif
ifeq ($(FIELDS_AVX2),1)
  # Force AVX2 implementation for fields
  CFLAGS += -DFIELDS_AVX2
endif
ifeq ($(FIELDS_AVX512),1)
  # Force AVX512 implementation for fields
  CFLAGS += -DFIELDS_AVX512
endif
ifeq ($(FIELDS_NEON),1)
  # ARM NEON implementation for fields (ARMv7 and AArch64)
  CFLAGS += -DFIELDS_NEON
  # On ARMv7, ensure NEON is enabled (AArch64 always has NEON)
  # Note: we use $(CC) alone (without CFLAGS) to detect the target architecture,
  # since CFLAGS may contain host-specific flags (e.g. -march=native) that are
  # invalid for cross-compilers targeting AArch64.
  DETECT_PLATFORM_AARCH64=$(shell $(CC) -dM -E - < /dev/null 2> /dev/null |egrep '__aarch64__|__ARM_ARCH_ISA_A64')
  ifeq ($(DETECT_PLATFORM_AARCH64),)
    CFLAGS += -mfpu=neon
  endif
endif
ifeq ($(USE_GF256_TABLE_MULT),1)
  # Use non-constant time GF(256) 65 kB table (in flash/ROM) multiplication
  CFLAGS += -DUSE_GF256_TABLE_MULT
  ifeq ($(GF256_MULT_TABLE_SRAM),1)
    # Large multiplication table forced to be in SRAM instead of flash/ROM
    CFLAGS += -DGF256_MULT_TABLE_SRAM
  endif
endif
ifeq ($(USE_GF256_TABLE_LOG_EXP),1)
  # Use log/exp tables in SRAM for GF(256) multiplication: should be constant
  # time on platforms with no cache to SRAM
  CFLAGS += -DUSE_GF256_TABLE_LOG_EXP
endif
ifeq ($(NO_FIELDS_REF_SWAR_OPT),1)
  # Force the fact that we do NOT use the SWAR (SIMD within a register) optimization for
  # fields reference implementation
  CFLAGS += -DNO_FIELDS_REF_SWAR_OPT
endif

ifeq ($(NO_GFNI),1)
  # Force NO GFNI automatic usage when detected
  CFLAGS += -DNO_GFNI
endif
# Adjust the benchmarking mode: by default we measure time unless stated
# otherwise
ifneq ($(NO_BENCHMARK_TIME),1)
  CFLAGS += -DBENCHMARK_TIME
endif
# Activate detailed benchmarking: fine-grained per-phase probes throughout
# BLC/PIOP (__BENCHMARK_START__/__BENCHMARK_STOP__). Adds real overhead to
# every probed phase, which pollutes a clean cost-per-grinding-trial
# measurement; use BENCHMARK_CYCLES alone (below) for that instead.
ifeq ($(BENCHMARK),1)
  CFLAGS += -DBENCHMARK -DBENCHMARK_CYCLES
endif
# Activate cycle-accurate top-level (KeyGen/Sign/Verify) timing on its own,
# without BENCHMARK's fine-grained probes.
ifeq ($(BENCHMARK_CYCLES),1)
  CFLAGS += -DBENCHMARK_CYCLES
endif
# Activate the grinding statistics section in bench
ifeq ($(BENCHMARK_GRINDING),1)
  CFLAGS += -DBENCHMARK_GRINDING
endif
# On Linux/x86, cycle counting normally uses perf_event_open + a direct
# userspace RDPMC read (fast, precise). STRICT_CYCLES=1 (default) makes
# ticks_setup() hard-fail (error + exit) if that fast path is unavailable
# (perf_event_open() itself fails, or the kernel/hardware doesn't grant
# direct RDPMC access) instead of silently falling back to a coarser,
# noisier cycle count (syscall-based read(), or raw RDTSC): a degraded
# measurement that looks like a real one is worse than an explicit failure.
# Opt out with STRICT_CYCLES=0 to accept the degraded fallback (with a
# warning on stderr) rather than failing.
STRICT_CYCLES ?= 1
ifeq ($(STRICT_CYCLES),1)
  CFLAGS += -DSTRICT_CYCLES
endif

# BLC SeedExpand cache:
#   default path: ON by default (auto-defined in blc_ct_default.c / blc_ot_default.c),
#                 opt-out via NO_BLC_SEEDEXPAND_CACHE=1
#   memopt path:  OFF by default, opt-in via BLC_SEEDEXPAND_CACHE=1
ifeq ($(BLC_SEEDEXPAND_CACHE),1)
  CFLAGS += -DBLC_SEEDEXPAND_CACHE
endif
ifeq ($(NO_BLC_SEEDEXPAND_CACHE),1)
  CFLAGS += -DNO_BLC_SEEDEXPAND_CACHE
endif

# Force the usage of only one Rijndael context for PRG and PRG_pub
# (only true for x1 variants, obviously nonsense for x2, x4 and x8 variants)
ifeq ($(PRG_ONE_RIJNDAEL_CTX),1)
  CFLAGS += -DPRG_ONE_RIJNDAEL_CTX
endif
# Memory optimized SeedCommit, only using one Rijndael context
ifeq ($(SEED_COMMIT_MEMOPT),1)
  CFLAGS += -DSEED_COMMIT_MEMOPT
endif

# Disable the PIOP cache for time / memory trade-off optimization
# The cache is activated by default
ifneq ($(USE_PIOP_CACHE),0)
  # VERIFY_MEMOPT and SIGN_MEMOPT imply MEMORY_EFFICIENT_PIOP too. They used to add
  # -DMEMORY_EFFICIENT_PIOP straight to CFLAGS further down, i.e. after this test,
  # so the guard stayed silent for them and only fired when the user also spelled
  # MEMORY_EFFICIENT_PIOP out explicitly. Test the three knobs here instead.
  ifneq ($(filter 1,$(MEMORY_EFFICIENT_PIOP) $(VERIFY_MEMOPT) $(SIGN_MEMOPT)),)
    # Error: USE_PIOP_CACHE and MEMORY_EFFICIENT_PIOP are not compatible
    $(error Error: USE_PIOP_CACHE and MEMORY_EFFICIENT_PIOP are not compatible! (VERIFY_MEMOPT and SIGN_MEMOPT imply MEMORY_EFFICIENT_PIOP))
  endif
  CFLAGS += -DUSE_PIOP_CACHE
endif
# Use the XOF x4 acceleration by default
ifneq ($(USE_XOF_X4),0)
  CFLAGS += -DUSE_XOF_X4
endif
# Use the XOF x8 acceleration: enabled by default on avx512 (native times8 kernel),
# disabled by default on other platforms (2 x x4 fallback has measurable overhead).
# Override with USE_XOF_X8=1 (force on) or USE_XOF_X8=0 (force off).
ifeq ($(USE_XOF_X8),1)
  CFLAGS += -DUSE_XOF_X8
else ifeq ($(USE_XOF_X8),0)
  # explicitly disabled, nothing to add
else ifeq ($(KECCAK_PLATFORM),avx512)
  CFLAGS += -DUSE_XOF_X8
else ifeq ($(KECCAK_PLATFORM),aarch64)
  # x8 via 2 x times4 (mlkem-native assembly) is faster than 8 sequential single perms
  CFLAGS += -DUSE_XOF_X8
endif
# Activate optimizing memory for the seed trees
ifeq ($(MEMORY_EFFICIENT_BLC),1)
  CFLAGS += -DMEMORY_EFFICIENT_BLC
endif
ifeq ($(BLC_DEFAULT_NO_KEEP_TREES),1)
  CFLAGS += -DBLC_DEFAULT_NO_KEEP_TREES
endif
# Useful parameters for memopt BLC
ifneq ($(GGMTREE_NB_ENC_CTX_IN_MEMORY),)
  CFLAGS += -DGGMTREE_NB_ENC_CTX_IN_MEMORY=$(GGMTREE_NB_ENC_CTX_IN_MEMORY)
endif
ifeq ($(SMALL_GGM_TREE_NO_BATCHING),1)
  CFLAGS += -DSMALL_GGM_TREE_NO_BATCHING
endif
ifneq ($(BLC_NB_LEAF_SEEDS_IN_PARALLEL),)
  CFLAGS += -DBLC_NB_LEAF_SEEDS_IN_PARALLEL=$(BLC_NB_LEAF_SEEDS_IN_PARALLEL)
endif
ifneq ($(SMALL_GGM_TREE_NB_SIMULTANEOUS_LEAVES_LOG),)
  CFLAGS += -DSMALL_GGM_TREE_NB_SIMULTANEOUS_LEAVES_LOG=$(SMALL_GGM_TREE_NB_SIMULTANEOUS_LEAVES_LOG)
endif
ifeq ($(BLC_SEEDCOMMIT_CACHE),1)
  CFLAGS += -DBLC_SEEDCOMMIT_CACHE
endif
ifneq ($(BLC_OT_BATCH_SIZE),)
  CFLAGS += -DBLC_OT_BATCH_SIZE=$(BLC_OT_BATCH_SIZE)
endif
ifneq ($(LARGE_GGM_TREE_INCR_BATCH),)
  CFLAGS += -DLARGE_GGM_TREE_INCR_BATCH=$(LARGE_GGM_TREE_INCR_BATCH)
endif
ifneq ($(LARGE_GGM_TREE_INCR_BATCH_VERIFY),)
  CFLAGS += -DLARGE_GGM_TREE_INCR_BATCH_VERIFY=$(LARGE_GGM_TREE_INCR_BATCH_VERIFY)
endif
# Slow folding: trade the NB_EVALS_LOG-sized folding scratch buckets (fast
# folding, default) for a direct per-leaf field-level accumulation (no extra
# buffer, but NB_EVALS field mults instead of NB_EVALS_LOG). Orthogonal to
# CT/OT. Defaults BLC_NB_LEAF_SEEDS_IN_PARALLEL to 1 when unset, but an
# explicit N > 1 is also supported (leaf_snapshot[N] in blc_memopt_folding.h
# trades N-1 extra acc-sized buffers for batched SeedExpand throughput - see
# blc_memopt.h).
ifeq ($(BLC_NO_FAST_FOLDING),1)
  CFLAGS += -DBLC_NO_FAST_FOLDING
endif


# Activate optimizing memory for PIOP
ifeq ($(MEMORY_EFFICIENT_PIOP),1)
  CFLAGS += -DMEMORY_EFFICIENT_PIOP
endif
ifneq ($(PIOP_NB_PARALLEL_REPETITIONS_SIGN),)
  CFLAGS += -DPIOP_NB_PARALLEL_REPETITIONS_SIGN=$(PIOP_NB_PARALLEL_REPETITIONS_SIGN)
endif
ifneq ($(PIOP_NB_PARALLEL_REPETITIONS_VERIFY),)
  CFLAGS += -DPIOP_NB_PARALLEL_REPETITIONS_VERIFY=$(PIOP_NB_PARALLEL_REPETITIONS_VERIFY)
endif
# Activate optimizing memory for Keygen
ifeq ($(MEMORY_EFFICIENT_KEYGEN),1)
  CFLAGS += -DMEMORY_EFFICIENT_KEYGEN
endif
ifeq ($(VERIFY_MEMOPT),1)
  CFLAGS += -DVERIFY_MEMOPT -DMEMORY_EFFICIENT_BLC -DMEMORY_EFFICIENT_PIOP
endif
ifeq ($(SIGN_MEMOPT),1)
  CFLAGS += -DSIGN_MEMOPT -DMEMORY_EFFICIENT_BLC -DMEMORY_EFFICIENT_PIOP
endif
# SIGN_MEMOPT_STREAM_COM1 / VERIFY_MEMOPT_STREAM_COM1 force the com1 streaming
# decision in Sign_memopt / Verify_memopt (0 = off, 1 = on). Left unset, each
# path decides on its own: streaming is on iff that path is batched, i.e.
# PIOP_NB_PARALLEL_REPETITIONS_SIGN/_VERIFY < TAU for CT, BLC_OT_BATCH_SIZE <
# TAU for OT. Output is byte-identical either way - only the stack profile
# changes. The two are set independently because signing and verification have
# separate batch parameters.
ifneq ($(SIGN_MEMOPT_STREAM_COM1),)
  CFLAGS += -DSIGN_MEMOPT_STREAM_COM1=$(SIGN_MEMOPT_STREAM_COM1)
endif
ifneq ($(VERIFY_MEMOPT_STREAM_COM1),)
  CFLAGS += -DVERIFY_MEMOPT_STREAM_COM1=$(VERIFY_MEMOPT_STREAM_COM1)
endif
# STREAM_VERIFY_BATCH controls how many executions StreamedVerify buffers
# between two RecomputePAlpha_partial_memopt calls (default:
# PIOP_NB_PARALLEL_REPETITIONS_VERIFY).
ifneq ($(STREAM_VERIFY_BATCH),)
  CFLAGS += -DSTREAM_VERIFY_BATCH=$(STREAM_VERIFY_BATCH)
endif
# Activate optimizing memory for PIOP with bitslicing
ifeq ($(PIOP_BITSLICE),1)
  CFLAGS += -DPIOP_BITSLICE
endif
# Opt OUT of the factorized handling of the b_hat row in the bitsliced
# verification PIOP. The optimization computes
# v_z = <A_i.v_x, v_x> + r*<b_i, v_x> instead of folding r*b_i into v_t first
ifeq ($(NO_PIOP_BITSLICE_OPT_VERIFY),1)
  CFLAGS += -DNO_PIOP_BITSLICE_OPT_VERIFY
endif
# Grinding algorithm: AES-based grinding (spec), the only supported algorithm.
# AES_GRINDING_X4: process 2 nonces per call (4 interleaved AES encryptions), on by default.
# Set NO_AES_GRINDING_X4=1 to use the scalar (single-nonce) AES path instead.
ifneq ($(NO_AES_GRINDING_X4),1)
  CFLAGS += -DAES_GRINDING_X4
endif
# Fields bitslice dedicated options
ifeq ($(FIELDS_BITSLICE_COMPOSITE),1)
  CFLAGS += -DFIELDS_BITSLICE_COMPOSITE
endif
ifeq ($(FIELDS_BITSLICE_PUBLIC_JUMP),1)
  CFLAGS += -DFIELDS_BITSLICE_PUBLIC_JUMP
endif
ifneq ($(BITSLICE_HYBRID_LEFTOVER_LIMIT),)
  CFLAGS += -DBITSLICE_HYBRID_LEFTOVER_LIMIT=$(BITSLICE_HYBRID_LEFTOVER_LIMIT)
endif

ifneq ($(USE_ENC_X8),0)
  CFLAGS += -DUSE_ENC_X8
endif
# BFS expansion for large OT GGM tree: on by default for OT variants.
# Set NO_LARGE_TREE_BFS=1 to revert to the DFS reference implementation.
# x8 batches are used automatically when the encryption backend provides them
# (USE_ENC_X8, itself on by default) since x8 consistently outperforms x4;
# set NO_LARGE_TREE_BFS_X8=1 to force the x4 batching path instead.
# Only the OT large-tree units read these, and those units compile to nothing on
# a CT build, so the flags are set unconditionally.
ifneq ($(NO_LARGE_TREE_BFS),1)
  CFLAGS += -DLARGE_TREE_BFS
  ifneq ($(NO_LARGE_TREE_BFS_X8),1)
    ifneq ($(USE_ENC_X8),0)
      CFLAGS += -DLARGE_TREE_BFS_X8
    endif
  endif
endif
# Contexts cleansing
ifeq ($(USE_ENC_CTX_CLEANSING),1)
  CFLAGS += -DUSE_ENC_CTX_CLEANSING
endif

# Do not use allocation probes
# Heap accounting probe (malloc redirection, common.h). Opt-in: it keeps an
# unlocked mutable global table, which makes Sign/Verify non-reentrant, and
# prints diagnostics from inside the crypto path. BENCHMARK=1 and
# BENCHMARK_CYCLES=1 switch it on too, since benchmark/bench.c is what consumes
# its output.
ifeq ($(USE_ALLOC_PROBE),1)
  CFLAGS += -DUSE_ALLOC_PROBE
endif
ifeq ($(NO_ALLOC_PROBE),1)
  CFLAGS += -DNO_ALLOC_PROBE
endif

# Stack + heap measurement via pthread canary (bench target only)
BENCH_EXTRA_LDFLAGS :=
ifeq ($(MEASURE_STACK),1)
  CFLAGS += -DMEASURE_STACK
  # -lpthread needed on Linux; macOS links pthread automatically via libSystem
  UNAME_S := $(shell uname -s)
  ifneq ($(UNAME_S),Darwin)
    BENCH_EXTRA_LDFLAGS += -lpthread
  endif
endif

# Use the signature buffer as temporary variable storage
ifeq ($(USE_SIGNATURE_BUFFER_AS_TEMP),1)
  CFLAGS += -DUSE_SIGNATURE_BUFFER_AS_TEMP
endif

ifeq ($(NO_NATIVE_TUNE),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
endif

## Toggles to force the platform compilation flags
# The mutually exclusive Rijndael backend flags, as enforced by rijndael.h. A
# FORCE_PLATFORM_* block that supplies a *default* backend must check this list
# first: adding one on top of a backend the caller already asked for trips the
# "are exclusive" #error instead of honouring the request.
RIJNDAEL_BACKEND_FLAGS = -DRIJNDAEL_TABLE -DRIJNDAEL_CONSTANT_TIME_REF -DRIJNDAEL_BITSLICE \
                         -DRIJNDAEL_EXTERNAL -DRIJNDAEL_AES_NI -DRIJNDAEL_VAES -DRIJNDAEL_ARM_AES

ifeq ($(FORCE_PLATFORM_REF),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  # Ref platform uses pure C fields implementation and Rijndael implementation.
  # Bitslice is only the default here: RIJNDAEL_TABLE and RIJNDAEL_CONSTANT_TIME_REF
  # are portable C backends too, and perfectly valid on this platform, so an
  # explicit choice must win rather than collide with the default.
  # Drop any field backend the auto-detection above may already have picked -
  # on an ARM target it sets -DFIELDS_NEON, and appending -DFIELDS_REF on top of
  # it now trips the exclusivity guard in fields.h. Symmetric to what the
  # FORCE_PLATFORM_AARCH64* blocks below do with -DFIELDS_REF.
  CFLAGS := $(subst -DFIELDS_NEON,,$(CFLAGS))
  CFLAGS += -DFIELDS_REF
ifeq ($(filter $(RIJNDAEL_BACKEND_FLAGS),$(CFLAGS)),)
  CFLAGS += -DRIJNDAEL_BITSLICE
endif
endif
ifeq ($(FORCE_PLATFORM_AVX2),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  CFLAGS += -maes -mavx2
endif
ifeq ($(FORCE_PLATFORM_AVX2_GFNI),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  CFLAGS += -maes -mgfni -mavx2
endif
# The *_VAES variants only add -mvaes: no -DRIJNDAEL_VAES is needed, and adding
# one would be wrong here. rijndael_platform.h picks the backend from __VAES__
# on its own (VAES > AES-NI > ARM AES > bitslice) and any explicit -DRIJNDAEL_*
# bypasses that auto-detection, so an explicit flag would also collide with a
# backend the caller asked for. The VAES sub-level follows from the rest of the
# ISA flags: RIJNDAEL_VAES256 here, RIJNDAEL_VAES512 in the AVX-512 blocks below.
ifeq ($(FORCE_PLATFORM_AVX2_VAES),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  CFLAGS += -maes -mvaes -mavx2
endif
ifeq ($(FORCE_PLATFORM_AVX2_VAES_GFNI),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  CFLAGS += -maes -mvaes -mgfni -mavx2
endif
ifeq ($(FORCE_PLATFORM_AVX512),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  CFLAGS += -maes -mavx512bw -mavx512f -mavx512vl -mavx512vpopcntdq -mavx512vbmi
endif
ifeq ($(FORCE_PLATFORM_AVX512_GFNI),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  CFLAGS += -maes -mgfni -mavx512bw -mavx512f -mavx512vl -mavx512vpopcntdq -mavx512vbmi
endif
# See the note above the AVX2 *_VAES blocks. -mvaes together with -mavx512f is
# what opens the 512-bit VAES forms (_mm512_aesenc_epi128), hence RIJNDAEL_VAES512.
ifeq ($(FORCE_PLATFORM_AVX512_VAES),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  CFLAGS += -maes -mvaes -mavx512bw -mavx512f -mavx512vl -mavx512vpopcntdq -mavx512vbmi
endif
ifeq ($(FORCE_PLATFORM_AVX512_VAES_GFNI),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  CFLAGS += -maes -mvaes -mgfni -mavx512bw -mavx512f -mavx512vl -mavx512vpopcntdq -mavx512vbmi
endif
ifeq ($(FORCE_PLATFORM_AARCH64),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  # AArch64 without crypto extension: NEON fields (always available), bitsliced Rijndael.
  # Auto-detection may have set -DFIELDS_REF if CC was invoked without aarch64 NEON visible;
  # strip it and enforce NEON fields explicitly.
  # Also strip any other Rijndael backend flags a combo may have added earlier (e.g.
  # RIJNDAEL_ARM_AES from the rijndael_arm_aes combo) to prevent conflicting -D flags that
  # trigger #error in rijndael.h.
  CFLAGS := $(subst -DFIELDS_REF,,$(CFLAGS))
  CFLAGS := $(filter-out -DRIJNDAEL_ARM_AES -DRIJNDAEL_AES_NI -DRIJNDAEL_VAES \
                         -DRIJNDAEL_TABLE -DRIJNDAEL_CONSTANT_TIME_REF,$(CFLAGS))
  CFLAGS += -DFIELDS_NEON -DRIJNDAEL_BITSLICE
  ifeq ($(KECCAK_PLATFORM),)
    KECCAK_PLATFORM = aarch64
  endif
endif
ifeq ($(FORCE_PLATFORM_AARCH64_AES),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  # AArch64 with ARMv8 crypto extension (AES+SHA1/2): hardware AES Rijndael, NEON fields.
  # Strip any conflicting Rijndael backend flags (e.g. -DRIJNDAEL_BITSLICE from the
  # rijndael_bitslice combo) to prevent the #error "exclusive" check in rijndael.h.
  CFLAGS := $(subst -DFIELDS_REF,,$(CFLAGS))
  CFLAGS := $(filter-out -DRIJNDAEL_BITSLICE -DRIJNDAEL_AES_NI -DRIJNDAEL_VAES \
                         -DRIJNDAEL_TABLE -DRIJNDAEL_CONSTANT_TIME_REF,$(CFLAGS))
  CFLAGS += -march=armv8-a+crypto -DFIELDS_NEON -DRIJNDAEL_ARM_AES
  ifeq ($(KECCAK_PLATFORM),)
    KECCAK_PLATFORM = aarch64
  endif
endif
ifeq ($(FORCE_PLATFORM_AARCH64_SHA3),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  # AArch64 with ARMv8.2 SHA3 extension (EOR3/RAX1/XAR): accelerated Keccak x4, bitsliced Rijndael.
  # Strip conflicting Rijndael backend flags for the same reason as FORCE_PLATFORM_AARCH64.
  CFLAGS := $(subst -DFIELDS_REF,,$(CFLAGS))
  CFLAGS := $(filter-out -DRIJNDAEL_ARM_AES -DRIJNDAEL_AES_NI -DRIJNDAEL_VAES \
                         -DRIJNDAEL_TABLE -DRIJNDAEL_CONSTANT_TIME_REF,$(CFLAGS))
  CFLAGS += -march=armv8-a+sha3 -DFIELDS_NEON -DRIJNDAEL_BITSLICE
  # Propagated to sha3 sub-make so KeccakP-1600-aarch64.c activates the SHA3 intrinsic path
  KECCAK_EXTRA_CFLAGS = -march=armv8-a+sha3
  ifeq ($(KECCAK_PLATFORM),)
    KECCAK_PLATFORM = aarch64
  endif
endif
ifeq ($(FORCE_PLATFORM_AARCH64_AES_SHA3),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  # AArch64 with ARMv8 crypto (AES) + ARMv8.2 SHA3: hardware AES Rijndael, accelerated Keccak x4.
  # Strip conflicting Rijndael backend flags for the same reason as FORCE_PLATFORM_AARCH64_AES.
  CFLAGS := $(subst -DFIELDS_REF,,$(CFLAGS))
  CFLAGS := $(filter-out -DRIJNDAEL_BITSLICE -DRIJNDAEL_AES_NI -DRIJNDAEL_VAES \
                         -DRIJNDAEL_TABLE -DRIJNDAEL_CONSTANT_TIME_REF,$(CFLAGS))
  CFLAGS += -march=armv8-a+crypto+sha3 -DFIELDS_NEON -DRIJNDAEL_ARM_AES
  # Propagated to sha3 sub-make so KeccakP-1600-aarch64.c activates the SHA3 intrinsic path
  KECCAK_EXTRA_CFLAGS = -march=armv8-a+crypto+sha3
  ifeq ($(KECCAK_PLATFORM),)
    KECCAK_PLATFORM = aarch64
  endif
endif
ifeq ($(FORCE_PLATFORM_ARM32_NEON),1)
  CFLAGS := $(subst -march=native,,$(CFLAGS))
  CFLAGS := $(subst -mcpu=native,,$(CFLAGS))
  CFLAGS := $(subst -mtune=native,,$(CFLAGS))
  # ARMv7A+NEON: NEON fields and instructions, bitsliced Rijndael.
  # Auto-detection without -mfpu=neon falls back to FIELDS_REF; strip it and set NEON explicitly.
  # Bitslice is a default here, same as FORCE_PLATFORM_REF above: this target has
  # no hardware AES, so a caller asking for table or constant-time-ref must be
  # honoured rather than overridden into an exclusive-backend #error.
  CFLAGS := $(subst -DFIELDS_REF,,$(CFLAGS))
  CFLAGS += -mfpu=neon -DFIELDS_NEON
ifeq ($(filter $(RIJNDAEL_BACKEND_FLAGS),$(CFLAGS)),)
  CFLAGS += -DRIJNDAEL_BITSLICE
endif
  ifeq ($(KECCAK_PLATFORM),)
    KECCAK_PLATFORM = arm32_neon
  endif
endif

# Externally provided XOF functions
ifeq ($(MQOM3_XOF_EXTERNAL_API),1)
  CFLAGS += -DMQOM3_XOF_EXTERNAL_API
endif

## Togles for various analysis and other useful stuff
# Static analysis of gcc
ifeq ($(FANALYZER),1)
  CFLAGS += -fanalyzer
endif
# Force Link Time Optimizations
# XXX: warning, this can be agressive and yield wrong results with -O3
ifeq ($(FLTO),1)
  CFLAGS += -flto
endif
# Use the sanitizers
ifeq ($(USE_SANITIZERS),1)
CFLAGS += -fsanitize=address -fsanitize=leak -fsanitize=undefined
  ifeq ($(USE_SANITIZERS_IGNORE_ALIGN),1)
    CFLAGS += -fno-sanitize=alignment
  endif
endif
ifeq ($(WERROR), 1)
  # Sometimes "-Werror" might be too much, we only use it when asked to
  CFLAGS += -Werror
endif
ifneq ($(PARAM_SECURITY),)
  # Adjust the security parameters as asked to
  CFLAGS += -DMQOM3_PARAM_SECURITY=$(PARAM_SECURITY)
endif

# "Weak" low-level API
ifeq ($(USE_WEAK_LOW_LEVEL_API),1)
  CFLAGS += -DUSE_WEAK_LOW_LEVEL_API
endif

# 'override' is required, not decorative: a variable passed as a make argument
# (make DESTINATION_PATH=... ) takes precedence over a plain ':=' assignment in the
# Makefile, so without it the separators below are silently dropped and every link
# target becomes <path><prefix><name> concatenated - with rc=0, which then makes a
# build script run whatever stale binary it finds under the intended name. Passing
# them through the environment (as manage.py does) was the only working form.
ifneq ($(DESTINATION_PATH),)
override DESTINATION_PATH := $(DESTINATION_PATH)/
endif
ifneq ($(PREFIX_EXEC),)
override PREFIX_EXEC := $(PREFIX_EXEC)_
endif

### Keccak library specific platfrom related flags
# If no platform is specified for Keccak, try to autodetect it
ifeq ($(KECCAK_PLATFORM),)
  KECCAK_DETECT_PLATFORM_AVX512VL=$(shell $(CC) $(CFLAGS) $(EXTRA_CFLAGS) -dM -E - < /dev/null 2> /dev/null |egrep AVX512VL)
  KECCAK_DETECT_PLATFORM_AVX512F=$(shell $(CC) $(CFLAGS) $(EXTRA_CFLAGS) -dM -E - < /dev/null 2> /dev/null |egrep AVX512F)
  KECCAK_DETECT_PLATFORM_SUB_AVX2=$(shell $(CC) $(CFLAGS) $(EXTRA_CFLAGS) -dM -E - < /dev/null 2> /dev/null |egrep AVX2)
  KECCAK_DETECT_PLATFORM_X64=$(shell $(CC) $(CFLAGS) $(EXTRA_CFLAGS) -dM -E - < /dev/null 2> /dev/null |egrep __x86_64__)
  KECCAK_DETECT_PLATFORM_AVX512=
  # NOTE: we detect __x86_64__ as our Keccak implementation specifically uses 64 bit registers in assembly
  # (while x86 32 bit platforms might support AVX2 or AVX-512)
  ifneq ($(KECCAK_DETECT_PLATFORM_X64),)
    ifneq ($(KECCAK_DETECT_PLATFORM_AVX512VL),)
      ifneq ($(KECCAK_DETECT_PLATFORM_AVX512F),)
        KECCAK_DETECT_PLATFORM_AVX512=1
      endif
    endif
  endif
  ifneq ($(KECCAK_DETECT_PLATFORM_X64),)
    ifneq ($(KECCAK_DETECT_PLATFORM_SUB_AVX2),)
        KECCAK_DETECT_PLATFORM_AVX2=1
    endif
  endif
  #
  ifneq ($(KECCAK_DETECT_PLATFORM_AVX512),)
      KECCAK_PLATFORM=avx512
  else
    ifneq ($(KECCAK_DETECT_PLATFORM_AVX2),)
      KECCAK_PLATFORM=avx2
    else
      # Possibly detect ARMv7M to use the assembly optimized version
      KECCAK_DETECT_PLATFORM_ARMV7M=$(shell $(CC) $(CFLAGS) $(EXTRA_CFLAGS) -dM -E - < /dev/null 2> /dev/null |egrep -e __ARM_ARCH_7M__ -e __ARM_ARCH_7EM__)
      ifneq ($(KECCAK_DETECT_PLATFORM_ARMV7M),)
          KECCAK_PLATFORM=armv7m
      else
          # Detect AArch64 (64-bit ARM): optimized opt64 single + mlkem-native x4 assembly
          KECCAK_DETECT_PLATFORM_AARCH64=$(shell $(CC) $(CFLAGS) $(EXTRA_CFLAGS) -dM -E - < /dev/null 2> /dev/null |egrep __aarch64__)
          ifneq ($(KECCAK_DETECT_PLATFORM_AARCH64),)
              KECCAK_PLATFORM=aarch64
          else
              # Detect ARMv7A+NEON (32-bit ARM with NEON): optimized single + x4 serial fallback
              # At this point we know it is not aarch64, so __ARM_NEON__ implies arm32.
              KECCAK_DETECT_PLATFORM_ARM32_NEON=$(shell $(CC) $(CFLAGS) $(EXTRA_CFLAGS) -dM -E - < /dev/null 2> /dev/null |egrep __ARM_NEON__)
              ifneq ($(KECCAK_DETECT_PLATFORM_ARM32_NEON),)
                  KECCAK_PLATFORM=arm32_neon
              else
                  # No specific platform detected, fallback to opt64
                  KECCAK_PLATFORM=opt64
              endif
          endif
      endif
    endif
  endif
endif
CFLAGS += -DKECCAK_PLATFORM="$(KECCAK_PLATFORM)"
# Propagate times8 kernel availability to main code (xof.h native path)
ifeq ($(KECCAK_PLATFORM),avx512)
  CFLAGS += -DXKCP_has_KeccakP1600times8
endif
# Adjust the include dir depending on the target platform
LIB_HASH_INCLUDES = $(LIB_HASH_DIR) $(LIB_HASH_DIR)/$(KECCAK_PLATFORM)
# aarch64 reuses opt64's single-perm SnP header - expose it to outer code as well
ifeq ($(KECCAK_PLATFORM),aarch64)
  LIB_HASH_INCLUDES += $(LIB_HASH_DIR)/opt64
endif
# arm32_neon: NEON assembly requires -mfpu=neon for the entire build to ensure
# consistent VFP/NEON ABI (vpush/vpop alignment); the sha3 Makefile already adds
# it for the sha3 objects, but the outer code must match to avoid stack alignment faults.
ifeq ($(KECCAK_PLATFORM),arm32_neon)
  CFLAGS += -mfpu=neon
endif

# Include the necessary headers
CFLAGS += $(foreach DIR, $(LIB_HASH_INCLUDES), -I$(DIR))
CFLAGS += $(foreach DIR, $(RIJNDAEL_INCLUDES), -I$(DIR))
CFLAGS += $(foreach DIR, $(GGM_INCLUDES), -I$(DIR))
CFLAGS += $(foreach DIR, $(BLC_INCLUDES), -I$(DIR))
CFLAGS += $(foreach DIR, $(PIOP_INCLUDES), -I$(DIR))
CFLAGS += $(foreach DIR, $(FIELDS_INCLUDES), -I$(DIR))
CFLAGS += $(foreach DIR, $(MQOM3_INCLUDES), -I$(DIR))

# MQOM Variant selection
MQOM3_VARIANT_CFLAGS=
### Cat 1 - CT (Correlated-Tree) variants
ifeq ($(MQOM3_VARIANT),cat1_gf2_shorter_ct)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=128
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=2
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=0
endif
ifeq ($(MQOM3_VARIANT),cat1_gf16_fast_ct)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=128
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=0
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=0
endif
ifeq ($(MQOM3_VARIANT),cat1_gf16_short_ct)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=128
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=0
endif
### Cat 1 - OT (One-Tree) variants
ifeq ($(MQOM3_VARIANT),cat1_gf2_shorter_ot)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=128
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=2
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=1
endif
ifeq ($(MQOM3_VARIANT),cat1_gf16_fast_ot)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=128
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=0
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=1
endif
ifeq ($(MQOM3_VARIANT),cat1_gf16_short_ot)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=128
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=1
endif
### Cat 3 - CT (Correlated-Tree) variants
ifeq ($(MQOM3_VARIANT),cat3_gf2_shorter_ct)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=192
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=2
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=0
endif
ifeq ($(MQOM3_VARIANT),cat3_gf16_fast_ct)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=192
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=0
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=0
endif
ifeq ($(MQOM3_VARIANT),cat3_gf16_short_ct)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=192
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=0
endif
### Cat 3 - OT (One-Tree) variants
ifeq ($(MQOM3_VARIANT),cat3_gf2_shorter_ot)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=192
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=2
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=1
endif
ifeq ($(MQOM3_VARIANT),cat3_gf16_fast_ot)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=192
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=0
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=1
endif
ifeq ($(MQOM3_VARIANT),cat3_gf16_short_ot)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=192
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=1
endif
### Cat 5 - CT (Correlated-Tree) variants
ifeq ($(MQOM3_VARIANT),cat5_gf2_shorter_ct)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=256
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=2
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=0
endif
ifeq ($(MQOM3_VARIANT),cat5_gf16_fast_ct)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=256
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=0
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=0
endif
ifeq ($(MQOM3_VARIANT),cat5_gf16_short_ct)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=256
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=0
endif
### Cat 5 - OT (One-Tree) variants
ifeq ($(MQOM3_VARIANT),cat5_gf2_shorter_ot)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=256
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=2
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=1
endif
ifeq ($(MQOM3_VARIANT),cat5_gf16_fast_ot)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=256
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=0
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=1
endif
ifeq ($(MQOM3_VARIANT),cat5_gf16_short_ot)
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_SECURITY=256
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_BASE_FIELD=4
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_TRADEOFF=1
  MQOM3_VARIANT_CFLAGS+=-DMQOM3_PARAM_OT_VARIANT=1
endif
################
# Guard: if MQOM3_VARIANT was explicitly set but matched nothing, raise an error
ifneq ($(MQOM3_VARIANT),)
  ifeq ($(MQOM3_VARIANT_CFLAGS),)
    $(error Unknown MQOM3_VARIANT '$(MQOM3_VARIANT)'. Valid variants: cat{1,3,5}_gf{2_shorter,16_fast,16_short}_{ct,ot})
  endif
endif
CFLAGS += $(MQOM3_VARIANT_CFLAGS)

# FLTO (link time optimizations) usage
ifeq ($(FLTO),1)
CFLAGS += -flto
LDFLAGS += -flto
endif

# Possibly append user provided extra CFLAGS
CFLAGS += $(EXTRA_CFLAGS)

# ASan's fake stack (its use-after-return detection) relocates frames into heap
# chunks that do not honour over-aligned locals. AVX-512 code has 64-byte
# aligned objects - the __m512i locals of the field backend - which the compiler
# then reads with vmovdqa64; that instruction faults outright when
# the frame it lands in is only 32-byte aligned, so the run dies on a SIGSEGV
# that has nothing to do with the code under test.
# Disable just that one ASan feature, and only where it bites: AVX-512 builds
# with sanitizers on. AVX2 needs 32-byte alignment, which the fake stack does
# provide, so it is deliberately left alone. Every other ASan check stays on.
# GCC exposes this only as a --param; -fsanitize-address-use-after-return is the
# Clang spelling and this compiler rejects it. There is no pragma or function
# attribute for it either: no_sanitize("use-after-return") is silently ignored,
# and only the blunt no_sanitize("address") exists, which would switch the whole
# sanitizer off for the function.
# Is the AVX-512 field backend actually in force? Testing for -DFIELDS_AVX512 is
# not enough: fields.h:84-96 auto-selects it whenever no FIELDS_* was named and
# the compiler targets the full subset it needs - which is exactly what happens
# under the default -march=native, and exactly the case that crashes. Mirror
# that condition here, with the same $(CC) -dM -E probe the Keccak detection
# above uses, run on the final CFLAGS since -march=native is what defines them.
FIELDS_AVX512_EFFECTIVE :=
ifneq ($(findstring -DFIELDS_AVX512,$(CFLAGS)),)
  FIELDS_AVX512_EFFECTIVE := 1
else
  ifeq ($(findstring -DFIELDS_REF,$(CFLAGS))$(findstring -DFIELDS_AVX2,$(CFLAGS))$(findstring -DFIELDS_NEON,$(CFLAGS)),)
    DETECT_FIELDS_AVX512 := $(shell $(CC) $(CFLAGS) -dM -E - < /dev/null 2>/dev/null | grep -cE "define __AVX512(BW|F|VL|VPOPCNTDQ|VBMI)__")
    ifeq ($(DETECT_FIELDS_AVX512),5)
      FIELDS_AVX512_EFFECTIVE := 1
    endif
  endif
endif

ifeq ($(USE_SANITIZERS),1)
  ifeq ($(FIELDS_AVX512_EFFECTIVE),1)
    ifeq ($(CLANG),1)
      CFLAGS += -fsanitize-address-use-after-return=never
    else
      CFLAGS += --param asan-use-after-return=0
    endif
  endif
endif

# Objects carry no record of the flags they were built with: -MMD -MP tracks
# header dependencies only, and no .o depends on $(CFLAGS).
# Hasher for the fingerprint. cksum is POSIX and present on Linux, macOS and the
# BSDs, but not universally (trimmed MSYS or busybox environments can lack it),
# and its absence is the dangerous case rather than a mere inconvenience:
# $(shell) then yields an empty string, the stamp name collapses to a constant,
# and the mechanism silently reverts to the stale-object behaviour it exists to
# prevent. So probe, fall back, and guard on the computed value rather than on
# the tool being installed - that also covers a hasher that exists but fails.
# "cut -d' ' -f1" suits all three: cksum prints "<crc> <bytes>", md5sum and
# sha1sum print "<hash>  -".
# Probe usability, not mere presence: a hasher can be on PATH and still fail
# (a stub, a broken install). Each candidate is run on a byte of input and
# kept only if it actually produces output.
FLAGS_HASHER := $(firstword $(foreach h,cksum md5sum sha1sum,$(if $(shell printf 'x' | $(h) 2>/dev/null),$(h))))
CFLAGS_FINGERPRINT := $(if $(FLAGS_HASHER),$(shell printf '%s' '$(CC) $(CFLAGS)' | $(FLAGS_HASHER) 2>/dev/null | cut -d' ' -f1))

# The "$(OBJS): $(CFLAGS_STAMP)" dependency below is an explicit rule, and it
# lands before "all:" in this file. Make picks its default goal from the first
# explicit rule whose target is not a dotted name, so that dependency would
# silently make "rijndael/rijndael_ref.o" the default goal and a bare "make"
# would build one object instead of everything. Pin the default goal here so
# it no longer depends on rule ordering.
.DEFAULT_GOAL := all

ifeq ($(CFLAGS_FINGERPRINT),)
  $(warning No usable cksum/md5sum/sha1sum: the flag-change rebuild trigger is OFF.)
  $(warning Run "make clean" yourself after changing any -D, or objects built under)
  $(warning the previous configuration get relinked into a mixed-ABI binary.)
else
CFLAGS_STAMP := .build-flags-$(CFLAGS_FINGERPRINT)

$(CFLAGS_STAMP):
	@rm -f .build-flags-*
	@touch $@

$(OBJS): $(CFLAGS_STAMP)
endif


KECCAK_OBJS_=$(shell cd sha3/ && CC="$(CC)" KECCAK_PLATFORM="$(KECCAK_PLATFORM)" make --no-print-directory print_objects)
KECCAK_OBJS=$(foreach OBJ, $(KECCAK_OBJS_),sha3/$(OBJ))

all: libhash $(OBJS)


libhash:
	@echo "[+] Compiling libhash"
	cd $(LIB_HASH_DIR) && KECCAK_PLATFORM="$(KECCAK_PLATFORM)" $(MAKE) CC="$(CC)" EXTRA_CFLAGS="$(KECCAK_EXTRA_CFLAGS) $(EXTRA_CFLAGS)"

.c.o:
	$(CC) $(CFLAGS) $(DEPFLAGS) -c -o $@ $<

.s.o:
	$(CC) $(CFLAGS) $(ASMFLAGS) $(DEPFLAGS) -c -o $@ $<

.S.o:
	$(CC) $(CFLAGS) $(ASMFLAGS) $(DEPFLAGS) -c -o $@ $<

sign: libhash $(OBJS)
	$(CC) $(CFLAGS) generator/PQCgenKAT_sign.c generator/rng.c $(OBJS) $(LIB_HASH) -lcrypto -o $(DESTINATION_PATH)$(PREFIX_EXEC)sign

kat_gen: libhash $(OBJS)
	$(CC) $(CFLAGS) generator/PQCgenKAT_sign.c generator/rng.c $(OBJS) $(LIB_HASH) -lcrypto -o $(DESTINATION_PATH)$(PREFIX_EXEC)kat_gen

kat_check: libhash $(OBJS)
	$(CC) $(CFLAGS) generator/PQCgenKAT_check.c generator/rng.c $(OBJS) $(LIB_HASH) -lcrypto -o $(DESTINATION_PATH)$(PREFIX_EXEC)kat_check

bench: libhash $(OBJS)
	$(CC) $(CFLAGS) benchmark/bench.c benchmark/timing.c $(OBJS) $(LIB_HASH) -lm $(BENCH_EXTRA_LDFLAGS) -o $(DESTINATION_PATH)$(PREFIX_EXEC)bench

bench_mem_keygen: libhash $(OBJS)
	$(CC) $(CFLAGS) benchmark/bench_mem_keygen.c $(OBJS) $(LIB_HASH) -lm -o $(DESTINATION_PATH)$(PREFIX_EXEC)bench_mem_keygen

bench_mem_sign: libhash $(OBJS)
	$(CC) $(CFLAGS) benchmark/bench_mem_sign.c $(OBJS) $(LIB_HASH) -lm -o $(DESTINATION_PATH)$(PREFIX_EXEC)bench_mem_sign

bench_mem_open: libhash $(OBJS)
	$(CC) $(CFLAGS) benchmark/bench_mem_open.c $(OBJS) $(LIB_HASH) -lm -o $(DESTINATION_PATH)$(PREFIX_EXEC)bench_mem_open

print_objects:
	@echo $(OBJS) && echo $(KECCAK_OBJS)

-include $(OBJS:.o=.d)

clean:
	@cd $(LIB_HASH_DIR) && make clean
	@find . -name "*.o" -type f -delete
	@find . -name "*.d" -type f -delete
	@find . -name "*.su" -type f -delete
	@find . -name "*.i" -type f -delete
	@rm -f kat_gen kat_check bench bench_mem_keygen bench_mem_sign bench_mem_open sign
	@rm -f .build-flags-*
