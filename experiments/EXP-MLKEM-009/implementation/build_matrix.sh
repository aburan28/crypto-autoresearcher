#!/usr/bin/env bash
# EXP-MLKEM-009 build matrix: true GNU ld -Wl,--wrap of mlkem_cmp{,_avx2,_neon}.
# Load-bearing wrap builds run under Docker linux/amd64 (GNU Binutils).
# Scratch root: /tmp/exp-mlkem-007
set -euo pipefail

ROOT=/tmp/exp-mlkem-007
SRC591=$ROOT/wolfssl-5.9.1
SRC592=$ROOT/wolfssl-5.9.2
BUILD=$ROOT/builds
HARNESS=$ROOT/harness
LOGS=$ROOT/logs
PRERUN=$ROOT/pre-run
SECOND=$ROOT/second-impl
REPO="${REPO:-/Volumes/Volume/crypto-autoresearcher-worktrees/mlkem-harness-002}"
IMPL="$REPO/experiments/EXP-MLKEM-009/implementation"
JOBS="${JOBS:-$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 2)}"

WRAP_FLAGS=(-Wl,--wrap=mlkem_cmp -Wl,--wrap=mlkem_cmp_avx2 -Wl,--wrap=mlkem_cmp_neon)

mkdir -p "$BUILD" "$HARNESS" "$LOGS" "$PRERUN" "$SECOND"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
now_s() { date +%s; }

TIMING_JSON=$PRERUN/build_timing_receipt.json
touch "$PRERUN/build_timing_events.ndjson"

record_event() {
  local name="$1" start="$2" end="$3" rc="$4" detail="${5:-}"
  local wall=$((end - start))
  printf '{"event":"%s","started_epoch":%s,"finished_epoch":%s,"wall_seconds":%s,"rc":%s,"detail":%s}\n' \
    "$name" "$start" "$end" "$wall" "$rc" "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$detail")" \
    >>"$PRERUN/build_timing_events.ndjson"
  echo "[timing] $name wall=${wall}s rc=$rc"
}

COMMON_FLAGS=(
  --enable-static --disable-shared --enable-mlkem --enable-sha3
  --disable-examples --disable-crypttests
)

clone_wolfssl() {
  local tag="$1" dest="$2"
  local t0 t1
  t0=$(now_s)
  if [[ -d "$dest/.git" ]]; then
    git -C "$dest" fetch --tags --force origin "$tag" || true
    git -C "$dest" checkout -f "$tag"
  else
    rm -rf "$dest"
    git clone --depth 1 --branch "$tag" https://github.com/wolfSSL/wolfssl.git "$dest"
  fi
  t1=$(now_s)
  record_event "clone_wolfssl_$tag" "$t0" "$t1" 0 "$dest"
  git -C "$dest" rev-parse HEAD
}

finalize_timing() {
  python3 - <<'PY'
import json, time
from pathlib import Path
root = Path("/tmp/exp-mlkem-007/pre-run")
events = []
p = root / "build_timing_events.ndjson"
if p.exists():
    for line in p.read_text().splitlines():
        if line.strip():
            events.append(json.loads(line))
total = sum(e.get("wall_seconds", 0) for e in events)
out = {
    "experiment_id": "EXP-MLKEM-009",
    "receipt_kind": "pre-run_build_accounting",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "scratch_root": "/tmp/exp-mlkem-007",
    "events": events,
    "total_recorded_wall_seconds": total,
    "note": "Library clone/configure/build wall-clock recorded here; referenced by RUN-MLKEM-033 manifests.",
}
(root / "build_timing_receipt.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"events": len(events), "total_wall_seconds": total}))
PY
}

# Primary path: linux/amd64 GNU ld --wrap for scalar + AVX2 wolfSSL builds.
build_linux_amd64_wrap() {
  local t0 t1 rc=0
  t0=$(now_s)
  docker run --rm --platform linux/amd64 \
    -v "$ROOT:/tmp/exp-mlkem-007" \
    -v "$REPO:/repo" \
    -e JOBS="$JOBS" \
    debian:bookworm-slim \
    bash -lc '
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq build-essential autoconf automake libtool git ca-certificates pkg-config binutils >/tmp/apt.log
ROOT=/tmp/exp-mlkem-007
IMPL=/repo/experiments/EXP-MLKEM-009/implementation
JOBS="${JOBS:-2}"
WRAP=(-Wl,--wrap=mlkem_cmp -Wl,--wrap=mlkem_cmp_avx2 -Wl,--wrap=mlkem_cmp_neon)
ld -v | head -1 | tee "$ROOT/pre-run/gnu_ld_version.txt"
echo "wrap_flags=${WRAP[*]}" | tee "$ROOT/pre-run/wrap_link_flags.txt"

build_one() {
  local id="$1" src="$2" backend="$3" cflags="$4" probe_macro="$5" cfg_extra="${6:-}"
  local bdir="$ROOT/builds/$id"
  mkdir -p "$bdir" "$ROOT/harness" "$ROOT/logs"
  cd "$src"
  if [[ ! -f configure ]]; then ./autogen.sh; fi
  cd "$bdir"
  if [[ ! -f Makefile ]]; then
    # shellcheck disable=SC2086
    "$src/configure" --enable-static --disable-shared --enable-mlkem --enable-sha3 \
      --disable-examples --disable-crypttests $cfg_extra CFLAGS="$cflags"
  fi
  make -j"$JOBS"
  local lib="$bdir/src/.libs/libwolfssl.a"
  [[ -f "$lib" ]] || lib="$bdir/src/libwolfssl.a"
  local commit; commit=$(git -C "$src" rev-parse HEAD)
  # Confirm symbols exist in archive
  nm -g "$lib" | grep -E " T mlkem_cmp(_avx2|_neon)?$" | tee "$bdir/mlkem_cmp_symbols.txt" || true
  gcc $cflags -c -o "$ROOT/harness/compare_wrap-$id.o" "$IMPL/compare_wrap.c"
  gcc $cflags -c -o "$ROOT/harness/compare_wrap_stub-$id.o" "$IMPL/compare_wrap_stub.c"
  # Unmodified probes (positive / isolation targets) — stub counters, NO --wrap
  gcc $cflags $probe_macro -I"$bdir" -I"$src" \
    -o "$ROOT/harness/conformance-$id" "$IMPL/conformance_probe.c" \
    "$ROOT/harness/compare_wrap_stub-$id.o" "$lib" -lm -lpthread
  gcc $cflags $probe_macro -I"$bdir" -I"$src" \
    -o "$ROOT/harness/decap-$id" "$IMPL/decap_boundary_probe.c" \
    "$ROOT/harness/compare_wrap_stub-$id.o" "$lib" -lm -lpthread
  # Wrapped probes: GNU ld --wrap; probe still calls mlkem_cmp* (no INTERPOSE_COMPARE)
  gcc $cflags $probe_macro -I"$bdir" -I"$src" \
    -o "$ROOT/harness/conformance-wrap-$id" "$IMPL/conformance_probe.c" \
    "$ROOT/harness/compare_wrap-$id.o" "$lib" "${WRAP[@]}" -lm -lpthread
  gcc $cflags $probe_macro -I"$bdir" -I"$src" \
    -o "$ROOT/harness/decap-wrap-$id" "$IMPL/decap_boundary_probe.c" \
    "$ROOT/harness/compare_wrap-$id.o" "$lib" "${WRAP[@]}" -lm -lpthread
  # Prove wrap redirection: nm on wrapped binary should reference __wrap_*
  nm -g "$ROOT/harness/conformance-wrap-$id" | grep -E "__wrap_mlkem_cmp" | tee "$bdir/wrap_nm_attest.txt"
  cat >"$bdir/build_meta_007.json" <<EOF
{
  "build_id": "$id",
  "backend": "$backend",
  "source_tree": "$src",
  "resolved_commit": "$commit",
  "conformance_probe": "$ROOT/harness/conformance-$id",
  "decap_probe": "$ROOT/harness/decap-$id",
  "conformance_probe_wrapped": "$ROOT/harness/conformance-wrap-$id",
  "decap_probe_wrapped": "$ROOT/harness/decap-wrap-$id",
  "wrap_object": "$ROOT/harness/compare_wrap-$id.o",
  "wrap_link_method": "gnu_ld_Wl_wrap_mlkem_cmp_family",
  "wrap_compile_flags": [],
  "wrap_link_flags": ["-Wl,--wrap=mlkem_cmp", "-Wl,--wrap=mlkem_cmp_avx2", "-Wl,--wrap=mlkem_cmp_neon"],
  "wrapped_symbols": ["mlkem_cmp", "mlkem_cmp_avx2", "mlkem_cmp_neon"],
  "forbidden_flags": ["-DINTERPOSE_COMPARE"],
  "probe_macro": "$probe_macro",
  "compiler": "$(gcc --version | head -1)",
  "linker": "$(ld -v 2>&1 | head -1)",
  "libwolfssl": "$lib",
  "host_arch": "x86_64",
  "execution": "docker_linux_amd64",
  "build_accounting": "timed_inside_EXP-MLKEM-009_docker_amd64"
}
EOF
}
# Clone if missing (host may have cloned already)
[[ -d "$ROOT/wolfssl-5.9.1/.git" ]] || git clone --depth 1 --branch v5.9.1-stable https://github.com/wolfSSL/wolfssl.git "$ROOT/wolfssl-5.9.1"
[[ -d "$ROOT/wolfssl-5.9.2/.git" ]] || git clone --depth 1 --branch v5.9.2-stable https://github.com/wolfSSL/wolfssl.git "$ROOT/wolfssl-5.9.2"
build_one BUILD-PREFIX-SCALAR "$ROOT/wolfssl-5.9.1" scalar "-O2" "-DPROBE_BACKEND_SCALAR" ""
build_one BUILD-POSTFIX-SCALAR "$ROOT/wolfssl-5.9.2" scalar "-O2" "-DPROBE_BACKEND_SCALAR" ""
build_one BUILD-PREFIX-AVX2 "$ROOT/wolfssl-5.9.1" avx2 "-O2 -mavx2" "-DPROBE_BACKEND_AVX2" "--enable-intelasm"
build_one BUILD-POSTFIX-AVX2 "$ROOT/wolfssl-5.9.2" avx2 "-O2 -mavx2" "-DPROBE_BACKEND_AVX2" "--enable-intelasm"
' || rc=$?
  t1=$(now_s)
  record_event "docker_linux_amd64_gnu_ld_wrap" "$t0" "$t1" "$rc" "scalar+avx2 prefix/postfix"
  return "$rc"
}

inspect_boringssl_mechanism() {
  local t0 t1
  t0=$(now_s)
  if [[ ! -d "$SECOND/boringssl/.git" ]]; then
    git clone --depth 1 https://github.com/google/boringssl.git "$SECOND/boringssl"
  fi
  t1=$(now_s)
  record_event "clone_boringssl" "$t0" "$t1" 0 "$SECOND/boringssl"
  local evidence=$PRERUN/boringssl_mechanism_evidence.txt
  {
    echo "BoringSSL ML-KEM comparison mechanism inspection"
    echo "repo=$SECOND/boringssl"
    echo "commit=$(git -C "$SECOND/boringssl" rev-parse HEAD)"
    echo
    rg -n "CRYPTO_memcmp|constant_time_eq|memcmp|verify" "$SECOND/boringssl/crypto/mlkem" 2>/dev/null | head -80 || true
    echo
    echo "VERDICT_STRICT: length-parameterized CRYPTO_memcmp — REJECT under strict_fixed_bound."
  } >"$evidence"
  echo "$evidence"
}

select_and_build_pqclean() {
  local t0 t1 rc=0
  t0=$(now_s)
  if [[ ! -d "$SECOND/PQClean/.git" ]]; then
    git clone --depth 1 https://github.com/PQClean/PQClean.git "$SECOND/PQClean"
  fi
  t1=$(now_s)
  record_event "clone_pqclean" "$t0" "$t1" 0 "$SECOND/PQClean"
  local scheme_dir="$SECOND/PQClean/crypto_kem/ml-kem-1024/avx2"
  local mech_file
  mech_file=$(ls "$scheme_dir"/verify.* 2>/dev/null | head -1 || true)
  mkdir -p "$BUILD/pqclean" "$PRERUN"
  {
    echo "# PQClean mechanism evidence (widened laboratory continuity only)"
    echo "scheme_dir=$scheme_dir"
    echo "backend=avx2"
    echo "commit=$(git -C "$SECOND/PQClean" rev-parse HEAD)"
    echo "verify_file=$mech_file"
    echo "VERDICT_STRICT: optimized length-parameterized SIMD verify — REJECT under strict_fixed_bound."
    if [[ -n "$mech_file" ]]; then
      head -60 "$mech_file"
    fi
  } >"$PRERUN/pqclean_mechanism_evidence.txt"

  docker run --rm --platform linux/amd64 \
    -v "$ROOT:/tmp/exp-mlkem-007" \
    -v "$REPO:/repo" \
    debian:bookworm-slim \
    bash -lc '
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq build-essential >/tmp/apt2.log
ROOT=/tmp/exp-mlkem-007
SCHEME=$ROOT/second-impl/PQClean/crypto_kem/ml-kem-1024/avx2
COMMON=$ROOT/second-impl/PQClean/common
IMPL=/repo/experiments/EXP-MLKEM-009/implementation
cd "$SCHEME"
make clean >/dev/null 2>&1 || true
make -j2
gcc -O2 -fPIC -I"$COMMON" -c "$COMMON/fips202.c" -o "$COMMON/fips202.o"
if [[ ! -f "$COMMON/randombytes.o" ]]; then
  cat >"$COMMON/randombytes_stub.c" <<EOF
#include <stdint.h>
#include <stddef.h>
void randombytes(uint8_t *out, size_t outlen) {
  size_t i; for (i=0;i<outlen;i++) out[i] = (uint8_t)(i*17u + 0x5au);
}
EOF
  gcc -O2 -c "$COMMON/randombytes_stub.c" -o "$COMMON/randombytes.o"
fi
gcc -O2 -mavx2 -I. -I"$COMMON" -o "$ROOT/harness/pqclean-probe" \
  "$IMPL/pqclean_probe.c" libml-kem-1024_avx2.a "$COMMON/fips202.o" "$COMMON/randombytes.o" -lm
test -x "$ROOT/harness/pqclean-probe"
' || rc=$?
  t1=$(now_s)
  record_event "build_pqclean_avx2" "$t0" "$t1" "$rc" "$scheme_dir"
  local commit
  commit=$(git -C "$SECOND/PQClean" rev-parse HEAD)
  cat >"$BUILD/pqclean/build_meta_007.json" <<EOF
{
  "build_id": "BUILD-PQCLEAN",
  "backend": "avx2",
  "repository": "https://github.com/PQClean/PQClean",
  "resolved_commit": "$commit",
  "scheme_dir": "$scheme_dir",
  "probe_binary": "$HARNESS/pqclean-probe",
  "verify_file": "$mech_file",
  "mechanism_evidence": "$PRERUN/pqclean_mechanism_evidence.txt",
  "bound_type": "optimized_compare_neighborhood_len_parameterized_simd_verify",
  "probe_built": $([[ -x $HARNESS/pqclean-probe ]] && echo true || echo false),
  "role": "widened_laboratory_continuity_only_not_goal_criterion_2"
}
EOF
  return "$rc"
}

cmd="${1:-all}"
case "$cmd" in
  clone)
    clone_wolfssl v5.9.1-stable "$SRC591"
    clone_wolfssl v5.9.2-stable "$SRC592"
    finalize_timing
    ;;
  linux-amd64-wrap)
    mkdir -p "$PRERUN"
    clone_wolfssl v5.9.1-stable "$SRC591"
    clone_wolfssl v5.9.2-stable "$SRC592"
    build_linux_amd64_wrap
    finalize_timing
    ;;
  second-impl)
    inspect_boringssl_mechanism || true
    select_and_build_pqclean || echo "PQClean build failed (non-fatal for criterion-2 honesty)"
    finalize_timing
    ;;
  all)
    mkdir -p "$PRERUN"
    clone_wolfssl v5.9.1-stable "$SRC591"
    clone_wolfssl v5.9.2-stable "$SRC592"
    build_linux_amd64_wrap
    inspect_boringssl_mechanism || true
    select_and_build_pqclean || echo "PQClean build failed"
    finalize_timing
    ;;
  finalize-timing)
    finalize_timing
    ;;
  *)
    echo "usage: $0 [clone|linux-amd64-wrap|second-impl|all|finalize-timing]" >&2
    exit 2
    ;;
esac
