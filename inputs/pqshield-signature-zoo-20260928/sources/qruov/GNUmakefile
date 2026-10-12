CC ?= cc
CFLAGS ?= -O3 -flto=auto -Wall -Wextra -Wpedantic
IMPL ?= opt
PARAM ?= 1q127L3
PRG ?= aes

IMPL_CHOICES := ref opt avx2
PARAM_CHOICES := \
	1q127L3 1q127L10 1q31L3 1q31L10 1q7L10 \
	3q127L3 3q127L10 3q31L3 3q31L10 3q7L10 \
	5q127L3 5q127L10 5q31L3 5q31L10 5q7L10
PRG_CHOICES := aes shake

ifeq ($(filter $(IMPL),$(IMPL_CHOICES)),)
$(error Unsupported IMPL='$(IMPL)' (supported: $(IMPL_CHOICES)))
endif
ifeq ($(filter $(PARAM),$(PARAM_CHOICES)),)
$(error Unsupported PARAM='$(PARAM)' (supported: $(PARAM_CHOICES)))
endif
ifeq ($(filter $(PRG),$(PRG_CHOICES)),)
$(error Unsupported PRG='$(PRG)' (supported: $(PRG_CHOICES)))
endif

BUILD_SUFFIX ?=
BUILD_DIR := build/$(IMPL)/$(PARAM)-$(PRG)$(BUILD_SUFFIX)
OPENSSL_PREFIX ?=
OPENSSL_LIBDIR ?=
OPENSSL_CFLAGS ?=
OPENSSL_LIBS ?= -lcrypto
SHA256SUM ?= $(shell if command -v sha256sum >/dev/null 2>&1; then echo sha256sum; elif command -v shasum >/dev/null 2>&1; then echo 'shasum -a 256'; else echo sha256sum; fi)

ifneq ($(strip $(OPENSSL_PREFIX)),)
OPENSSL_CFLAGS += -I$(OPENSSL_PREFIX)/include
ifeq ($(strip $(OPENSSL_LIBDIR)),)
ifneq ($(wildcard $(OPENSSL_PREFIX)/lib64),)
OPENSSL_LIBDIR := $(OPENSSL_PREFIX)/lib64
else
OPENSSL_LIBDIR := $(OPENSSL_PREFIX)/lib
endif
endif
OPENSSL_LIBS := -L$(OPENSSL_LIBDIR) $(OPENSSL_LIBS)
endif

IMPL_SRCS_ref := src/ref/qruov.c
IMPL_SRCS_opt := src/opt/qruov.c src/opt/emi_transform.c src/opt/emi_transform_gen.c
IMPL_SRCS_avx2 := src/avx2/qruov.c src/avx2/emi_transform.c src/avx2/emi_matrix.c src/avx2/emi_transform_gen.c src/avx2/helpers.c src/avx2/kernel.c src/avx2/x86aesni.c
SIGN_COMMON_SRCS := src/sign.c src/qruov_common.c src/qrop.c src/rng.c src/prg.c src/prim.c src/linsys.c

IMPL_CFLAGS_ref :=
IMPL_CFLAGS_opt :=
IMPL_CFLAGS_avx2 := -mavx2 -mbmi2 -maes -DPRIM_AES_BACKEND_X86AESNI=1

TEST_CFLAGS_ref :=
TEST_CFLAGS_opt := -DQRUOV_HAS_EMI_TRANSFORM=1
TEST_CFLAGS_avx2 := -DQRUOV_HAS_EMI_TRANSFORM=1
TEST_EXTRA_SRCS_ref :=
TEST_EXTRA_SRCS_opt := src/opt/emi_matrix.c
TEST_EXTRA_SRCS_avx2 :=

PRG_CFLAGS_aes := -DPRG_IS_AES=1
PRG_CFLAGS_shake := -DPRG_IS_AES=0

IMPL_CFLAGS := $(IMPL_CFLAGS_$(IMPL))
TEST_CFLAGS := $(TEST_CFLAGS_$(IMPL))
TEST_EXTRA_SRCS := $(TEST_EXTRA_SRCS_$(IMPL))
PRG_CFLAGS := $(PRG_CFLAGS_$(PRG))
PARAM_CFLAGS := -DQRUOV_PARAM_$(PARAM)

COMMON_SIGN_SRCS := $(SIGN_COMMON_SRCS) $(IMPL_SRCS_$(IMPL))

BASE_CFLAGS := $(CFLAGS) $(IMPL_CFLAGS) $(PRG_CFLAGS) $(PARAM_CFLAGS) -Isrc -Isrc/$(IMPL) $(OPENSSL_CFLAGS)

.PHONY: all test bench valgrind kat PQCgenKAT_sign generate-emi-transform generate-kat-for-impl generate-nist-submission generate-supercop check-kat clean help print-config

all: print-config $(BUILD_DIR)/PQCgenKAT_sign

help:
	@echo "Targets:"
	@echo "  make [all]           Build PQCgenKAT_sign in $(BUILD_DIR)"
	@echo "  make test            Build and run combined tests"
	@echo "  make bench           Build and run benchmark"
	@echo "  make valgrind        Run quick bench sanity under valgrind (COUNT=1)"
	@echo "  make kat             Build and run PQCgenKAT_sign in $(BUILD_DIR)"
	@echo "  make PQCgenKAT_sign  Build KAT generator"
	@echo "  make check-kat       Check KAT generator hash against $(KAT_REF_FILE)"
	@echo "  make clean           Remove build/ and $(NIST_SUBMISSION_DIR)/"
	@echo "  make generate-emi-transform    Regenerate EMI generated sources and emi_transform.h from tools/genmat.py"
	@echo "  make generate-kat-for-impl     Generate all KAT files for IMPL=$(IMPL) and make checksums build/$(IMPL)/KAT_SHA256SUMS.txt"
	@echo "  make generate-nist-submission  Create NIST-style submission tree at $(NIST_SUBMISSION_DIR)"
	@echo "  make generate-supercop         Create SUPERCOP-style tree at $(SUPERCOP_SUBMISSION_DIR)"
	@echo
	@echo "Variables (override with VAR=value):"
	@printf "  CC=%s\t(primary C compiler)\n" "$(CC)"
	@printf "  IMPL=%s\tchoices: %s\n" "$(IMPL)" "$(IMPL_CHOICES)"
	@printf "  PARAM=%s\tchoices: %s\n" "$(PARAM)" "$(PARAM_CHOICES)"
	@printf "  PRG=%s\tchoices: %s\n" "$(PRG)" "$(PRG_CHOICES)"
	@echo "  OPENSSL_PREFIX=$(OPENSSL_PREFIX)"
	@echo "  OPENSSL_LIBDIR=$(OPENSSL_LIBDIR)"
	@printf "  VALGRIND=%s\t(for valgrind)\n" "$(VALGRIND)"
	@printf "  VALGRIND_OPTS=%s\t(for valgrind)\n" "$(VALGRIND_OPTS)"
	@printf "  KAT_REF_FILE=%s\t(for check-kat)\n" "$(KAT_REF_FILE)"
	@printf "  SHA256SUM=%s\t(for KAT hashing)\n" "$(SHA256SUM)"
	@printf "  KAT_PARAMS='%s'\t(for generate-kat-for-impl)\n" "$(KAT_PARAMS)"
	@printf "  KAT_PRGS='%s'\t(for generate-kat-for-impl)\n" "$(KAT_PRGS)"
	@echo
	@echo "Examples:"
	@echo "  make test"
	@echo "  make IMPL=ref kat"
	@echo "  make IMPL=avx2 PARAM=1q127L10 PRG=aes bench"
	@echo "  make IMPL=opt PARAM=1q127L10 PRG=aes valgrind"
	@echo "  make IMPL=ref KAT_PARAMS='1q127L3 1q127L10 1q31L10' KAT_PRGS='aes shake' generate-kat-for-impl"
	@echo "  ./tools/ci.sh CI"
	@echo "  ./tools/ci.sh RELEASE   # slow full sweep"

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/test: $(COMMON_SIGN_SRCS) test/test.c test/linsys_round2_ref.c test/linsys_round2_ref.h $(TEST_EXTRA_SRCS) | $(BUILD_DIR)
	$(CC) $(BASE_CFLAGS) $(COMMON_SIGN_SRCS) test/test.c test/linsys_round2_ref.c $(TEST_EXTRA_SRCS) $(TEST_CFLAGS) $(OPENSSL_LIBS) -o $@

$(BUILD_DIR)/bench: $(COMMON_SIGN_SRCS) test/bench.c | $(BUILD_DIR)
	$(CC) $(BASE_CFLAGS) $^ $(OPENSSL_LIBS) -o $@

$(BUILD_DIR)/PQCgenKAT_sign: $(COMMON_SIGN_SRCS) src/PQCgenKAT_sign.c | $(BUILD_DIR)
	$(CC) $(BASE_CFLAGS) $^ $(OPENSSL_LIBS) -o $@

print-config:
	@echo "IMPL=$(IMPL) PARAM=$(PARAM) PRG=$(PRG)"

test: print-config $(BUILD_DIR)/test
	"$(BUILD_DIR)/test"

bench: print-config $(BUILD_DIR)/bench
	"$(BUILD_DIR)/bench"

VALGRIND ?= valgrind
VALGRIND_OPTS ?= --quiet --error-exitcode=1

valgrind: print-config $(BUILD_DIR)/bench
	COUNT=1 $(VALGRIND) $(VALGRIND_OPTS) "$(BUILD_DIR)/bench" keygen sign verify

PQCgenKAT_sign: print-config $(BUILD_DIR)/PQCgenKAT_sign

kat: print-config $(BUILD_DIR)/PQCgenKAT_sign
	(cd "$(BUILD_DIR)" && ./PQCgenKAT_sign >/dev/null)

generate-emi-transform:
	python3 tools/genmat.py avx2-matrix.c > src/avx2/emi_matrix.c
	python3 tools/genmat.py avx2-transform_gen.c > src/avx2/emi_transform_gen.c
	python3 tools/genmat.py opt-transform_gen.c > src/opt/emi_transform_gen.c
	python3 tools/genmat.py opt-matrix.c > src/opt/emi_matrix.c
	python3 tools/genmat.py emi_transform.h > src/avx2/emi_transform.h
	python3 tools/genmat.py emi_transform.h > src/opt/emi_transform.h

KAT_OUT_ROOT ?= build/$(IMPL)
KAT_SHA256_FILE := $(KAT_OUT_ROOT)/KAT_SHA256SUMS.txt
KAT_PARAMS ?= $(PARAM_CHOICES)
KAT_PRGS ?= $(PRG_CHOICES)

generate-kat-for-impl:
	mkdir -p $(KAT_OUT_ROOT)
	find $(KAT_OUT_ROOT) -type f \( -name 'PQCsignKAT_*.req' -o -name 'PQCsignKAT_*.rsp' \) -delete
	@PARAM_CHOICES='$(KAT_PARAMS)' PRG_CHOICES='$(KAT_PRGS)' \
	./tools/all.sh $(MAKE) -B IMPL=$(IMPL) OPENSSL_PREFIX='$(OPENSSL_PREFIX)' kat
	(cd $(KAT_OUT_ROOT) && find . -mindepth 2 -maxdepth 2 -type f -name 'PQCsignKAT_*.rsp' | sed 's#^\./##' | sort | xargs $(SHA256SUM)) > $(KAT_SHA256_FILE)
	@echo "wrote $(KAT_SHA256_FILE)"

NIST_SUBMISSION_DIR := QRUOV_Round3_Submission
NIST_KAT_SRCS_ref := $(notdir $(SIGN_COMMON_SRCS) $(IMPL_SRCS_ref)) PQCgenKAT_sign.c
NIST_KAT_SRCS_opt := $(notdir $(SIGN_COMMON_SRCS) $(IMPL_SRCS_opt)) PQCgenKAT_sign.c
NIST_KAT_SRCS_avx2 := $(notdir $(SIGN_COMMON_SRCS) $(IMPL_SRCS_avx2)) PQCgenKAT_sign.c

generate-nist-submission:
	@NIST_SUBMISSION_DIR='$(NIST_SUBMISSION_DIR)' \
	PARAM_CHOICES='$(PARAM_CHOICES)' \
	PRG_CHOICES='$(PRG_CHOICES)' \
	DEFAULT_PARAM='$(PARAM)' \
	DEFAULT_PRG='$(PRG)' \
	NIST_IMPL_CFLAGS_REF='$(IMPL_CFLAGS_ref)' \
	NIST_IMPL_CFLAGS_OPT='$(IMPL_CFLAGS_opt)' \
	NIST_IMPL_CFLAGS_AVX2='$(IMPL_CFLAGS_avx2)' \
	NIST_KAT_SRCS_REF='$(NIST_KAT_SRCS_ref)' \
	NIST_KAT_SRCS_OPT='$(NIST_KAT_SRCS_opt)' \
	NIST_KAT_SRCS_AVX2='$(NIST_KAT_SRCS_avx2)' \
	./tools/generate-nist-submission.sh

SUPERCOP_SUBMISSION_DIR := QRUOV_SUPERCOP

generate-supercop:
	@SUPERCOP_SUBMISSION_DIR='$(SUPERCOP_SUBMISSION_DIR)' \
	SUPERCOP_PARAM_CHOICES='$(PARAM_CHOICES)' \
	SUPERCOP_PRG_CHOICES='$(PRG_CHOICES)' \
	SUPERCOP_IMPL_CHOICES='$(IMPL_CHOICES)' \
	SUPERCOP_CC='$(CC)' \
	SUPERCOP_CFLAGS='$(CFLAGS)' \
	SUPERCOP_PRG_CFLAGS_AES='$(PRG_CFLAGS_aes)' \
	SUPERCOP_PRG_CFLAGS_SHAKE='$(PRG_CFLAGS_shake)' \
	./tools/generate-supercop.sh

KAT_REF_FILE ?= test/KAT_SHA256SUMS.txt
KAT_CHECK_BUILD_DIR ?= $(BUILD_DIR)-katcheck

check-kat:
	@set -e; \
	katdir="$(abspath $(KAT_CHECK_BUILD_DIR))"; \
	tmpdir=$$(mktemp -d /tmp/qruov-kat-XXXXXX); \
	trap 'rm -rf "$$tmpdir"' EXIT; \
	find "$$katdir" -type f \( -name 'PQCsignKAT_*.req' -o -name 'PQCsignKAT_*.rsp' \) -delete 2>/dev/null || true; \
	$(MAKE) -B BUILD_DIR='$(KAT_CHECK_BUILD_DIR)' IMPL=$(IMPL) PARAM=$(PARAM) PRG=$(PRG) OPENSSL_PREFIX='$(OPENSSL_PREFIX)' kat >/dev/null; \
	find "$$katdir" -type f -name 'PQCsignKAT_*.req' -delete; \
	$(SHA256SUM) "$$katdir"/PQCsignKAT_*.rsp | sed "s#  $$katdir/#  $(PARAM)-$(PRG)/#" > "$$tmpdir/KAT_SHA256SUMS.txt"; \
	ref_line="$(PARAM)-$(PRG)/PQCsignKAT_32.rsp"; \
	grep "  $$ref_line$$" "$(KAT_REF_FILE)" > "$$tmpdir/ref.txt"; \
	diff -u "$$tmpdir/ref.txt" "$$tmpdir/KAT_SHA256SUMS.txt"; \
	echo "KAT hash matches: IMPL=$(IMPL) PARAM=$(PARAM) PRG=$(PRG)"

clean:
	rm -rf build $(NIST_SUBMISSION_DIR) $(SUPERCOP_SUBMISSION_DIR)
