CC?=gcc
AR?=ar
WARNING_FLAGS?=-Wall -Wextra -Wpedantic -Wno-unused-function

CFLAGS?= -O3 $(CFLAGS_PLATFORM) $(WARNING_FLAGS) -std=gnu99
CFLAGS+=$(EXTRA_CFLAGS) $(EXTRA_WARNING_FLAGS)
# Kept separate so $(shell $(CC) $(CFLAGS) ...) detection commands don't generate "-.d".
DEPFLAGS = -MMD -MP

# Do we have a C++ compiler instead of a C compiler?
GPP := $(shell $(CROSS_COMPILE)$(CC) -v 2>&1 | grep g++)
CLANGPP := $(shell echo $(CROSS_COMPILE)$(CC) | grep clang++)
ifneq ($(GPP),)
CFLAGS := $(patsubst -std=gnu99, -std=gnu++2a, $(CFLAGS))
endif
ifneq ($(CLANGPP),)
CFLAGS := $(patsubst -std=gnu99, -std=gnu++2a, $(CFLAGS))
CFLAGS += -Wno-deprecated
endif

CFLAGS += -DNO_MISALIGNED_ACCESSES

# "Weak" low-level API
ifeq ($(USE_WEAK_LOW_LEVEL_API),1)
  CFLAGS += -DUSE_WEAK_LOW_LEVEL_API
endif

COMMON_SOURCES=KeccakHash.c KeccakSponge.c KeccakSpongetimes4.c KeccakHashtimes4.c
COMMON_OBJECTS=KeccakHash.o KeccakSponge.o KeccakSpongetimes4.o KeccakHashtimes4.o

ifeq ($(KECCAK_PLATFORM),avx512)
	INCLUDE_PATHS=avx512
	SPECIFIC_SOURCES=avx512/KeccakP-1600-AVX512.S avx512/KeccakP-1600-times4-SIMD512.c avx512/KeccakP-1600-times8-AVX512.c
	SPECIFIC_OBJECTS=avx512/KeccakP-1600-AVX512.o avx512/KeccakP-1600-times4-SIMD512.o avx512/KeccakP-1600-times8-AVX512.o
	PLATFORM=1
	CFLAGS_PLATFORM += -mavx512vl -mavx512f
	CFLAGS += -DXKCP_has_KeccakP1600times8
	COMMON_SOURCES += KeccakSpongetimes8.c KeccakHashtimes8.c
	COMMON_OBJECTS += KeccakSpongetimes8.o KeccakHashtimes8.o
endif
ifeq ($(KECCAK_PLATFORM),avx2)
	INCLUDE_PATHS=avx2
	SPECIFIC_SOURCES=avx2/KeccakP-1600-AVX2.S avx2/KeccakP-1600-times4-SIMD256.c
	SPECIFIC_OBJECTS=avx2/KeccakP-1600-AVX2.o avx2/KeccakP-1600-times4-SIMD256.o
	PLATFORM=1
	CFLAGS_PLATFORM += -mavx2
endif
ifeq ($(KECCAK_PLATFORM),opt64)
	INCLUDE_PATHS=opt64
	SPECIFIC_SOURCES=opt64/KeccakP-1600-opt64.c opt64/KeccakP-1600-times4-on1.c
	SPECIFIC_OBJECTS=opt64/KeccakP-1600-opt64.o opt64/KeccakP-1600-times4-on1.o
	PLATFORM=1
endif
ifeq ($(KECCAK_PLATFORM),plain32)
	INCLUDE_PATHS=plain32
	SPECIFIC_SOURCES=plain32/KeccakP-1600-inplace32BI.c plain32/KeccakP-1600-times4-on1.c
	SPECIFIC_OBJECTS=plain32/KeccakP-1600-inplace32BI.o plain32/KeccakP-1600-times4-on1.o
	PLATFORM=1
endif
ifeq ($(KECCAK_PLATFORM),armv7m)
	INCLUDE_PATHS=armv7m
	SPECIFIC_SOURCES=armv7m/keccakp1600_balanced_cortexm3-4.S armv7m/KeccakP-1600-times4-on1.c
	SPECIFIC_OBJECTS=armv7m/keccakp1600_balanced_cortexm3-4.o armv7m/KeccakP-1600-times4-on1.o
	PLATFORM=1
endif
ifeq ($(KECCAK_PLATFORM),aarch64)
	# Single permutation: AArch64 C implementation with optional ARMv8.2+SHA3 intrinsics.
	#   - __ARM_FEATURE_SHA3 defined: uses RAX1 (θ D-computation) and BCAX (χ step).
	#   - otherwise: delegates to opt64/KeccakP-1600-opt64.c (included at compile time).
	# Times4: ARMv8-A scalar+NEON hybrid from mlkem-native (Becker-Kannwischer);
	#         v84a variant auto-selected by the C file when __ARM_FEATURE_SHA3 is defined.
	INCLUDE_PATHS=aarch64 opt64
	SPECIFIC_SOURCES=aarch64/KeccakP-1600-aarch64.c \
	                 aarch64/KeccakP-1600-times4-armv8a.c \
	                 aarch64/KeccakP-1600-times4-x4-v8a-asm.S \
	                 aarch64/KeccakP-1600-times4-x4-v84a-asm.S
	SPECIFIC_OBJECTS=aarch64/KeccakP-1600-aarch64.o \
	                 aarch64/KeccakP-1600-times4-armv8a.o \
	                 aarch64/KeccakP-1600-times4-x4-v8a-asm.o \
	                 aarch64/KeccakP-1600-times4-x4-v84a-asm.o
	PLATFORM=1
endif
ifeq ($(KECCAK_PLATFORM),arm32_neon)
	# Single permutation: ARMv7A+NEON optimized assembly.
	# Times4: serial fallback (PlSnP-Fallback.inc), stride=224 bytes (aligned to 32).
	INCLUDE_PATHS=arm32_neon
	SPECIFIC_SOURCES=arm32_neon/KeccakP-1600-armv7a-le-neon-gcc.s \
	                 arm32_neon/KeccakP-1600-times4-on1.c
	SPECIFIC_OBJECTS=arm32_neon/KeccakP-1600-armv7a-le-neon-gcc.o \
	                 arm32_neon/KeccakP-1600-times4-on1.o
	PLATFORM=1
	CFLAGS_PLATFORM += -mfpu=neon
endif

# Use the sanitizers
ifeq ($(USE_SANITIZERS),1)
CFLAGS += -fsanitize=address -fsanitize=leak -fsanitize=undefined
  # XXX: NOTE: we must remove the signed integers overflows from the
  # sanitizers since we "abuse" them in the arithmetic library
  CFLAGS += -fno-sanitize=signed-integer-overflow
  ifeq ($(USE_SANITIZERS_IGNORE_ALIGN),1)
    CFLAGS += -fno-sanitize=alignment
  endif
endif

ifeq ($(WERROR), 1)
  # Sometimes "-Werror" might be too much, we only use it when asked to
  CFLAGS += -Werror
endif

HEADERS_INCLUDE=$(patsubst %,-I./%,$(INCLUDE_PATHS))
SOURCES=$(COMMON_SOURCES) $(SPECIFIC_SOURCES)
OBJECTS=$(COMMON_OBJECTS) $(SPECIFIC_OBJECTS)

# flag-fingerprint stamp
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

# The "$(OBJECTS): $(CFLAGS_STAMP)" dependency below is an explicit rule, and it
# lands before "all:" in this file. Make picks its default goal from the first
# explicit rule whose target is not a dotted name, so that dependency would
# silently make "KeccakHash.o" the default goal and the parent Makefile's
# "libhash" target - which invokes this one with no explicit goal - would stop
# after one object, never producing libhash.a. Pin the default goal here so it
# no longer depends on rule ordering.
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

$(OBJECTS): $(CFLAGS_STAMP)
endif

SHA3LIB=libhash.a

%.o : %.c
ifneq ($(PLATFORM),1)
	$(error "Sorry: no platform specified ... Please select KECCAK_PLATFORM=avx512, or avx2, or opt64, or aarch64, or plain32, or armv7m, or arm32_neon")
endif
	$(CC) $(CFLAGS) $(DEPFLAGS) -c -I. $(HEADERS_INCLUDE) $< -o $@

all: $(SOURCES) $(SHA3LIB)


$(SHA3LIB): $(OBJECTS)
	$(AR) rcs $@ $^

%.o : %.S
	$(CC) $(CFLAGS) $(DEPFLAGS) -c $< -o $@

%.o : %.s
	$(CC) $(CFLAGS) $(DEPFLAGS) -c $< -o $@

-include $(COMMON_OBJECTS:.o=.d) $(SPECIFIC_OBJECTS:.o=.d)

headers:
	@echo HEADERS=$(INCLUDE_PATHS)

print_objects:
	@echo $(OBJECTS)

clean:
	rm $(COMMON_OBJECTS) $(SPECIFIC_OBJECTS) 2>/dev/null || true
	find . -name "*.d" -type f -delete 2>/dev/null || true
	rm $(SHA3LIB) 2>/dev/null || true
	rm -f .build-flags-* 2>/dev/null || true
