#!/usr/bin/env bash
# EXP-MLKEM-006 build matrix. All clones/builds under /tmp/exp-mlkem-006.
# Records wall-clock in /tmp/exp-mlkem-006/pre-run/build_timing_receipt.json
set -euo pipefail

ROOT=/tmp/exp-mlkem-006
SRC591=$ROOT/wolfssl-5.9.1
SRC592=$ROOT/wolfssl-5.9.2
BUILD=$ROOT/builds
HARNESS=$ROOT/harness
LOGS=$ROOT/logs
PRERUN=$ROOT/pre-run
SECOND=$ROOT/second-impl
REPO="${REPO:-/Volumes/Volume/crypto-autoresearcher-worktrees/mlkem-harness-002}"
IMPL="$REPO/experiments/EXP-MLKEM-006/implementation"
JOBS="${JOBS:-$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 2)}"

mkdir -p "$BUILD" "$HARNESS" "$LOGS" "$PRERUN" "$SECOND"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
now_s() { date +%s; }

TIMING_JSON=$PRERUN/build_timing_receipt.json
# Append-only timing log across staged invocations; do not wipe prior events.
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

configure_build_wolf() {
  local id="$1" src="$2" extra_cfg="$3"
  local bdir="$BUILD/$id"
  local t0 t1 rc=0
  mkdir -p "$bdir"
  t0=$(now_s)
  (
    cd "$src"
    if [[ ! -f configure ]]; then
      ./autogen.sh
    fi
  )
  (
    cd "$bdir"
    if [[ ! -f Makefile ]]; then
      # shellcheck disable=SC2086
      "$src/configure" --prefix="$bdir/install" "${COMMON_FLAGS[@]}" $extra_cfg
    fi
    make -j"$JOBS"
  ) >"$LOGS/build-$id.log" 2>&1 || rc=$?
  t1=$(now_s)
  record_event "build_wolfssl_$id" "$t0" "$t1" "$rc" "$extra_cfg"
  return "$rc"
}

compile_wolf_probes() {
  local id="$1"
  local backend="$2"
  local src="$3"
  local bdir="$BUILD/$id"
  local commit
  commit=$(git -C "$src" rev-parse HEAD)
  local inc="-I$bdir -I$src"
  local lib="$bdir/src/.libs/libwolfssl.a"
  [[ -f "$lib" ]] || lib="$bdir/src/libwolfssl.a"
  [[ -f "$lib" ]] || { echo "missing lib for $id"; return 1; }

  local probe_macro="-DPROBE_BACKEND_SCALAR"
  local cc=clang
  local cflags=(-O2)
  local link_extra=(-lm -lpthread)
  case "$backend" in
    scalar) probe_macro="-DPROBE_BACKEND_SCALAR" ;;
    neon)
      probe_macro="-DPROBE_BACKEND_NEON"
      ;;
    avx2)
      probe_macro="-DPROBE_BACKEND_AVX2"
      # AVX2 probes are produced inside the amd64 docker build path.
      ;;
  esac

  echo "[probe] $id conformance+decap (+wrapped) ($cc $probe_macro)"
  # Unmodified probes (positive / isolation targets)
  "$cc" "${cflags[@]}" $probe_macro $inc \
    -o "$HARNESS/conformance-$id" "$IMPL/conformance_probe.c" "$lib" "${link_extra[@]}"
  "$cc" "${cflags[@]}" $probe_macro $inc \
    -o "$HARNESS/decap-$id" "$IMPL/decap_boundary_probe.c" "$lib" "${link_extra[@]}"

  # Call-site wrapper probes: -DINTERPOSE_COMPARE + compare_wrap.o (Darwin-safe)
  "$cc" "${cflags[@]}" -c -o "$HARNESS/compare_wrap-$id.o" "$IMPL/compare_wrap.c"
  "$cc" "${cflags[@]}" $probe_macro -DINTERPOSE_COMPARE $inc \
    -o "$HARNESS/conformance-wrap-$id" "$IMPL/conformance_probe.c" \
    "$HARNESS/compare_wrap-$id.o" "$lib" "${link_extra[@]}"
  "$cc" "${cflags[@]}" $probe_macro $inc \
    -o "$HARNESS/decap-wrap-$id" "$IMPL/decap_boundary_probe.c" \
    "$lib" "${link_extra[@]}"

  cat >"$bdir/build_meta_006.json" <<EOF
{
  "build_id": "$id",
  "backend": "$backend",
  "source_tree": "$src",
  "resolved_commit": "$commit",
  "conformance_probe": "$HARNESS/conformance-$id",
  "decap_probe": "$HARNESS/decap-$id",
  "conformance_probe_wrapped": "$HARNESS/conformance-wrap-$id",
  "decap_probe_wrapped": "$HARNESS/decap-wrap-$id",
  "wrap_object": "$HARNESS/compare_wrap-$id.o",
  "wrap_link_method": "call_site_wrapper_INTERPOSE_COMPARE",
  "wrap_compile_flags": ["-DINTERPOSE_COMPARE"],
  "wrapped_symbols": ["library_cmp->mlkem_interposed_defective_compare"],
  "probe_macro": "$probe_macro",
  "compiler": "$("$cc" --version | head -1)",
  "libwolfssl": "$lib",
  "host_arch": "$(uname -m)",
  "build_accounting": "timed_inside_EXP-MLKEM-006_pre-run_or_RUN-MLKEM-021"
}
EOF
}

build_avx2_via_docker() {
  local t0 t1 rc=0
  t0=$(now_s)
  docker run --rm --platform linux/amd64 \
    -v "$ROOT:/tmp/exp-mlkem-006" \
    -v "$REPO:/repo" \
    -e JOBS="$JOBS" \
    debian:bookworm-slim \
    bash -lc '
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq build-essential autoconf automake libtool git ca-certificates pkg-config >/tmp/apt.log
ROOT=/tmp/exp-mlkem-006
IMPL=/repo/experiments/EXP-MLKEM-006/implementation
JOBS="${JOBS:-2}"
build_one() {
  local id="$1" src="$2"
  local bdir="$ROOT/builds/$id"
  mkdir -p "$bdir"
  # Fresh build dir if prior configure failed
  if [[ -f "$bdir/config.log" ]] && ! [[ -f "$bdir/Makefile" ]]; then
    rm -rf "$bdir"
    mkdir -p "$bdir"
  fi
  cd "$src"
  if [[ ! -f configure ]]; then ./autogen.sh; fi
  cd "$bdir"
  if [[ ! -f Makefile ]]; then
    "$src/configure" --enable-static --disable-shared --enable-mlkem --enable-sha3 \
      --disable-examples --disable-crypttests --enable-intelasm CFLAGS="-O2 -mavx2" \
      || "$src/configure" --enable-static --disable-shared --enable-mlkem --enable-sha3 \
      --disable-examples --disable-crypttests CFLAGS="-O2 -mavx2 -DUSE_INTEL_SPEEDUP"
  fi
  make -j"$JOBS"
  local lib="$bdir/src/.libs/libwolfssl.a"
  [[ -f "$lib" ]] || lib="$bdir/src/libwolfssl.a"
  local commit; commit=$(git -C "$src" rev-parse HEAD)
  gcc -O2 -mavx2 -c -o "$ROOT/harness/compare_wrap-$id.o" "$IMPL/compare_wrap.c"
  gcc -O2 -mavx2 -DPROBE_BACKEND_AVX2 -I"$bdir" -I"$src" \
    -o "$ROOT/harness/conformance-$id" "$IMPL/conformance_probe.c" "$lib" -lm -lpthread
  gcc -O2 -mavx2 -DPROBE_BACKEND_AVX2 -I"$bdir" -I"$src" \
    -o "$ROOT/harness/decap-$id" "$IMPL/decap_boundary_probe.c" "$lib" -lm -lpthread
  gcc -O2 -mavx2 -DPROBE_BACKEND_AVX2 -DINTERPOSE_COMPARE -I"$bdir" -I"$src" \
    -o "$ROOT/harness/conformance-wrap-$id" "$IMPL/conformance_probe.c" \
    "$ROOT/harness/compare_wrap-$id.o" "$lib" -lm -lpthread
  gcc -O2 -mavx2 -DPROBE_BACKEND_AVX2 -I"$bdir" -I"$src" \
    -o "$ROOT/harness/decap-wrap-$id" "$IMPL/decap_boundary_probe.c" \
    "$lib" -lm -lpthread
  cat >"$bdir/build_meta_006.json" <<EOF
{
  "build_id": "$id",
  "backend": "avx2",
  "source_tree": "$src",
  "resolved_commit": "$commit",
  "conformance_probe": "$ROOT/harness/conformance-$id",
  "decap_probe": "$ROOT/harness/decap-$id",
  "conformance_probe_wrapped": "$ROOT/harness/conformance-wrap-$id",
  "decap_probe_wrapped": "$ROOT/harness/decap-wrap-$id",
  "wrap_object": "$ROOT/harness/compare_wrap-$id.o",
  "wrap_link_method": "call_site_wrapper_INTERPOSE_COMPARE",
  "wrap_compile_flags": ["-DINTERPOSE_COMPARE"],
  "wrap_link_flags": [],
  "wrapped_symbols": ["library_cmp->mlkem_interposed_defective_compare"],
  "probe_macro": "-DPROBE_BACKEND_AVX2",
  "compiler": "$(gcc --version | head -1)",
  "libwolfssl": "$lib",
  "host_arch": "x86_64",
  "execution": "docker_linux_amd64",
  "build_accounting": "timed_inside_EXP-MLKEM-006_docker_amd64"
}
EOF
}
build_one BUILD-PREFIX-AVX2 "$ROOT/wolfssl-5.9.1"
build_one BUILD-POSTFIX-AVX2 "$ROOT/wolfssl-5.9.2"
' || rc=$?
  t1=$(now_s)
  record_event "docker_amd64_avx2_builds" "$t0" "$t1" "$rc" "BUILD-PREFIX-AVX2,BUILD-POSTFIX-AVX2"
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
    echo "VERDICT_STRICT: length-parameterized CRYPTO_memcmp — REJECT under strict_fixed_bound. Eligible only under widened_optimized_compare if selected as W2/W3, not as silent fixed-bound stand-in."
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

  local scheme_dir=""
  local backend=""
  local mech_file=""
  # EXP-MLKEM-006 widened default peer W1: PQClean ml-kem-1024 avx2 verify.
  # Prefer avx2 (docker) so criterion_used=widened_optimized_compare can pin W1.
  if [[ -d "$SECOND/PQClean/crypto_kem/ml-kem-1024/avx2" ]]; then
    scheme_dir="$SECOND/PQClean/crypto_kem/ml-kem-1024/avx2"
    backend="avx2"
  elif [[ -d "$SECOND/PQClean/crypto_kem/ml-kem-1024/aarch64" ]]; then
    scheme_dir="$SECOND/PQClean/crypto_kem/ml-kem-1024/aarch64"
    backend="aarch64"
  else
    echo "No avx2/aarch64 ML-KEM-1024 backend in PQClean" >&2
    return 1
  fi

  mech_file=$(ls "$scheme_dir"/verify.* 2>/dev/null | head -1 || true)
  mkdir -p "$BUILD/pqclean" "$PRERUN"
  {
    echo "# PQClean mechanism evidence"
    echo "scheme_dir=$scheme_dir"
    echo "backend=$backend"
    echo "commit=$(git -C "$SECOND/PQClean" rev-parse HEAD)"
    echo "verify_file=$mech_file"
    if [[ -n "$mech_file" ]]; then
      echo "--- head of verify ---"
      head -80 "$mech_file"
      echo "--- bound / vector markers ---"
      rg -n "vmovd|vpxor|ld1|veor|CRYPTO_BYTES|1568|49|loop|rep" "$mech_file" | head -40 || true
    fi
  } >"$PRERUN/pqclean_mechanism_evidence.txt"

  t0=$(now_s)
  if [[ "$backend" == "aarch64" ]]; then
    (
      cd "$scheme_dir"
      make clean >/dev/null 2>&1 || true
      make -j"$JOBS"
      local objs
      objs=$(ls ./*.o 2>/dev/null | tr '\n' ' ')
      # shellcheck disable=SC2086
      clang -O2 -I. -o "$HARNESS/pqclean-probe" "$IMPL/pqclean_probe.c" $objs -lm
    ) >"$LOGS/build-pqclean.log" 2>&1 || rc=$?
  else
    # avx2 via docker amd64
    docker run --rm --platform linux/amd64 \
      -v "$ROOT:/tmp/exp-mlkem-006" \
      -v "$REPO:/repo" \
      debian:bookworm-slim \
      bash -lc '
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq build-essential >/tmp/apt2.log
ROOT=/tmp/exp-mlkem-006
SCHEME=$ROOT/second-impl/PQClean/crypto_kem/ml-kem-1024/avx2
COMMON=$ROOT/second-impl/PQClean/common
IMPL=/repo/experiments/EXP-MLKEM-006/implementation
cd "$SCHEME"
make clean >/dev/null 2>&1 || true
make -j2
# common fips202 + randombytes
gcc -O2 -fPIC -I"$COMMON" -c "$COMMON/fips202.c" -o "$COMMON/fips202.o"
gcc -O2 -fPIC -I"$COMMON" -c "$COMMON/randombytes.c" -o "$COMMON/randombytes.o" 2>/dev/null || \
  gcc -O2 -fPIC -I"$COMMON" -c "$COMMON/../test/common/randombytes.c" -o "$COMMON/randombytes.o" 2>/dev/null || true
if [[ ! -f "$COMMON/randombytes.o" ]]; then
  # minimal deterministic RNG stub for probe only (not a crypto claim)
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
  fi
  t1=$(now_s)
  record_event "build_pqclean_$backend" "$t0" "$t1" "$rc" "$scheme_dir"

  local commit
  commit=$(git -C "$SECOND/PQClean" rev-parse HEAD)
  if [[ -x "$HARNESS/pqclean-probe" ]]; then
    cat >"$BUILD/pqclean/build_meta_006.json" <<EOF
{
  "build_id": "BUILD-PQCLEAN",
  "backend": "$backend",
  "repository": "https://github.com/PQClean/PQClean",
  "resolved_commit": "$commit",
  "scheme_dir": "$scheme_dir",
  "probe_binary": "$HARNESS/pqclean-probe",
  "verify_file": "$mech_file",
  "mechanism_evidence": "$PRERUN/pqclean_mechanism_evidence.txt",
  "bound_type": "optimized_compare_neighborhood_len_parameterized_simd_verify",
  "probe_built": true
}
EOF
  else
    echo "pqclean-probe missing after build (rc=$rc)" >&2
    cat >"$BUILD/pqclean/build_meta_006.json" <<EOF
{
  "build_id": "BUILD-PQCLEAN",
  "backend": "$backend",
  "repository": "https://github.com/PQClean/PQClean",
  "resolved_commit": "$commit",
  "scheme_dir": "$scheme_dir",
  "probe_binary": "$HARNESS/pqclean-probe",
  "verify_file": "$mech_file",
  "mechanism_evidence": "$PRERUN/pqclean_mechanism_evidence.txt",
  "bound_type": "optimized_compare_neighborhood_len_parameterized_simd_verify",
  "probe_built": false,
  "build_rc": $rc
}
EOF
    rc=1
  fi
  return "$rc"
}

finalize_timing() {
  python3 - <<'PY'
import json, time
from pathlib import Path
root = Path("/tmp/exp-mlkem-006/pre-run")
events = []
p = root / "build_timing_events.ndjson"
if p.exists():
    for line in p.read_text().splitlines():
        if line.strip():
            events.append(json.loads(line))
total = sum(e.get("wall_seconds", 0) for e in events)
out = {
    "experiment_id": "EXP-MLKEM-006",
    "receipt_kind": "pre-run_build_accounting",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "scratch_root": "/tmp/exp-mlkem-006",
    "events": events,
    "total_recorded_wall_seconds": total,
    "note": "Library clone/configure/build wall-clock is recorded here and referenced by RUN-MLKEM-021 manifests. No silent reuse of prior experiment builds.",
}
(root / "build_timing_receipt.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"events": len(events), "total_wall_seconds": total}))
PY
}

cmd="${1:-all}"
case "$cmd" in
  clone)
    clone_wolfssl v5.9.1-stable "$SRC591"
    clone_wolfssl v5.9.2-stable "$SRC592"
    finalize_timing
    ;;
  native-wolf)
    # Native arm64: scalar (+ neon if armasm enables)
    configure_build_wolf BUILD-PREFIX-SCALAR "$SRC591" ""
    configure_build_wolf BUILD-POSTFIX-SCALAR "$SRC592" ""
    configure_build_wolf BUILD-PREFIX-NEON "$SRC591" "--enable-armasm" || echo "NEON prefix configure/build failed"
    configure_build_wolf BUILD-POSTFIX-NEON "$SRC592" "--enable-armasm" || echo "NEON postfix configure/build failed"
    compile_wolf_probes BUILD-PREFIX-SCALAR scalar "$SRC591"
    compile_wolf_probes BUILD-POSTFIX-SCALAR scalar "$SRC592"
    compile_wolf_probes BUILD-PREFIX-NEON neon "$SRC591" || echo "NEON prefix probe failed"
    compile_wolf_probes BUILD-POSTFIX-NEON neon "$SRC592" || echo "NEON postfix probe failed"
    finalize_timing
    ;;
  avx2-docker)
    build_avx2_via_docker
    finalize_timing
    ;;
  second-impl)
    inspect_boringssl_mechanism || true
    select_and_build_pqclean
    finalize_timing
    ;;
  all)
    clone_wolfssl v5.9.1-stable "$SRC591"
    clone_wolfssl v5.9.2-stable "$SRC592"
    configure_build_wolf BUILD-PREFIX-SCALAR "$SRC591" ""
    configure_build_wolf BUILD-POSTFIX-SCALAR "$SRC592" ""
    configure_build_wolf BUILD-PREFIX-NEON "$SRC591" "--enable-armasm" || echo "NEON prefix failed (infra)"
    configure_build_wolf BUILD-POSTFIX-NEON "$SRC592" "--enable-armasm" || echo "NEON postfix failed (infra)"
    compile_wolf_probes BUILD-PREFIX-SCALAR scalar "$SRC591"
    compile_wolf_probes BUILD-POSTFIX-SCALAR scalar "$SRC592"
    compile_wolf_probes BUILD-PREFIX-NEON neon "$SRC591" || echo "NEON prefix probe failed"
    compile_wolf_probes BUILD-POSTFIX-NEON neon "$SRC592" || echo "NEON postfix probe failed"
    build_avx2_via_docker || echo "AVX2 docker build failed (infra)"
    inspect_boringssl_mechanism || true
    select_and_build_pqclean || echo "PQClean build failed"
    finalize_timing
    ;;
  finalize-timing)
    finalize_timing
    ;;
  *)
    echo "usage: $0 [clone|native-wolf|avx2-docker|second-impl|all|finalize-timing]" >&2
    exit 2
    ;;
esac
