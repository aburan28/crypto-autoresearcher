#!/usr/bin/env bash
# EXP-MLKEM-003 build matrix. Scratch under /tmp/exp-mlkem-003 only.
set -euo pipefail

ROOT=/tmp/exp-mlkem-003
SRC591=$ROOT/wolfssl-5.9.1
SRC592=$ROOT/wolfssl-5.9.2
BUILD=$ROOT/builds
HARNESS=$ROOT/harness
IMPL=/workspace/experiments/EXP-MLKEM-003/implementation
JOBS="${JOBS:-$(nproc 2>/dev/null || echo 2)}"
LOGS=$ROOT/logs

mkdir -p "$BUILD" "$HARNESS" "$LOGS"

COMMON_FLAGS=(
  --enable-static --disable-shared --enable-mlkem --enable-sha3
  --disable-examples --disable-crypttests
)

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
  local cc=gcc
  local link_extra=(-lm -lpthread)
  case "$backend" in
    scalar) probe_macro="-DPROBE_BACKEND_SCALAR" ;;
    avx2) probe_macro="-DPROBE_BACKEND_AVX2" ;;
    neon)
      probe_macro="-DPROBE_BACKEND_NEON"
      cc=aarch64-linux-gnu-gcc
      ;;
  esac

  echo "[probe] $id conformance+decap ($cc $probe_macro)"
  "$cc" -O2 $probe_macro $inc \
    -o "$HARNESS/conformance-$id" "$IMPL/conformance_probe.c" "$lib" "${link_extra[@]}"
  "$cc" -O2 $probe_macro $inc \
    -o "$HARNESS/decap-$id" "$IMPL/decap_boundary_probe.c" "$lib" "${link_extra[@]}"

  cat >"$bdir/build_meta_003.json" <<EOF
{
  "build_id": "$id",
  "backend": "$backend",
  "source_tree": "$src",
  "resolved_commit": "$commit",
  "conformance_probe": "$HARNESS/conformance-$id",
  "decap_probe": "$HARNESS/decap-$id",
  "probe_macro": "$probe_macro",
  "compiler": "$("$cc" --version | head -1)",
  "libwolfssl": "$lib"
}
EOF
}

build_liboqs_probe() {
  local commit
  commit=$(git -C "$ROOT/second-impl/liboqs" rev-parse HEAD)
  local inc="-I$BUILD/liboqs/include"
  local lib="$BUILD/liboqs/lib/liboqs.a"
  echo "[probe] liboqs"
  gcc -O2 $inc -o "$HARNESS/liboqs-probe" "$IMPL/liboqs_probe.c" "$lib" -lm -lpthread
  cat >"$BUILD/liboqs/build_meta_003.json" <<EOF
{
  "build_id": "BUILD-LIBOQS",
  "backend": "liboqs_avx2_dispatch",
  "repository": "https://github.com/open-quantum-safe/liboqs",
  "tag": "0.12.0",
  "resolved_commit": "$commit",
  "probe_binary": "$HARNESS/liboqs-probe",
  "liboqs": "$lib"
}
EOF
}

cmd="${1:-probes}"
case "$cmd" in
  probes-x86)
    compile_wolf_probes BUILD-PREFIX-SCALAR scalar "$SRC591"
    compile_wolf_probes BUILD-PREFIX-AVX2 avx2 "$SRC591"
    compile_wolf_probes BUILD-POSTFIX-SCALAR scalar "$SRC592"
    compile_wolf_probes BUILD-POSTFIX-AVX2 avx2 "$SRC592"
    ;;
  probes-neon)
    compile_wolf_probes BUILD-PREFIX-NEON neon "$SRC591"
    compile_wolf_probes BUILD-POSTFIX-NEON neon "$SRC592"
    ;;
  liboqs)
    build_liboqs_probe
    ;;
  all)
    compile_wolf_probes BUILD-PREFIX-SCALAR scalar "$SRC591"
    compile_wolf_probes BUILD-PREFIX-AVX2 avx2 "$SRC591"
    compile_wolf_probes BUILD-POSTFIX-SCALAR scalar "$SRC592"
    compile_wolf_probes BUILD-POSTFIX-AVX2 avx2 "$SRC592"
    compile_wolf_probes BUILD-PREFIX-NEON neon "$SRC591" || echo "NEON probe compile failed (infra)"
    compile_wolf_probes BUILD-POSTFIX-NEON neon "$SRC592" || echo "NEON probe compile failed (infra)"
    build_liboqs_probe
    ;;
  *)
    echo "usage: $0 [probes-x86|probes-neon|liboqs|all]" >&2
    exit 2
    ;;
esac
