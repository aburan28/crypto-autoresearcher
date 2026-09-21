#!/usr/bin/env bash
# EXP-MLKEM-002 build matrix. Scratch trees live under /tmp/exp-mlkem-002 only.
set -euo pipefail

ROOT=/tmp/exp-mlkem-002
SRC591=$ROOT/wolfssl-5.9.1
SRC592=$ROOT/wolfssl-5.9.2
BUILD=$ROOT/builds
PROBE_SRC="${PROBE_SRC:-/workspace/experiments/EXP-MLKEM-002/implementation/comparison_probe.c}"
JOBS="${JOBS:-$(nproc 2>/dev/null || echo 2)}"

mkdir -p "$BUILD" "$ROOT/logs" "$ROOT/harness"

COMMON_FLAGS=(
  --enable-static
  --disable-shared
  --enable-mlkem
  --enable-sha3
  --disable-examples
  --disable-crypttests
)

build_one() {
  local id="$1"
  local src="$2"
  local backend="$3"   # scalar|avx2|neon
  local host="${4:-}"
  local bdir="$BUILD/$id"
  local log="$ROOT/logs/build-$id.log"
  mkdir -p "$bdir"
  echo "[build] $id backend=$backend host=${host:-native}" | tee "$log"

  local conf=("${COMMON_FLAGS[@]}")
  local cflags="-O2 -fvisibility=hidden"
  local probe_macro="-DPROBE_BACKEND_SCALAR"
  local cross=()

  case "$backend" in
    scalar)
      conf+=(--disable-asm --disable-intelasm --disable-armasm --disable-aesni)
      probe_macro="-DPROBE_BACKEND_SCALAR"
      ;;
    avx2)
      conf+=(--enable-intelasm --enable-asm)
      probe_macro="-DPROBE_BACKEND_AVX2"
      ;;
    neon)
      conf+=(--enable-armasm --enable-asm --disable-intelasm)
      probe_macro="-DPROBE_BACKEND_NEON"
      cross=(--host=aarch64-linux-gnu)
      ;;
    *)
      echo "unknown backend $backend" >&2; return 2
      ;;
  esac

  (
    cd "$bdir"
    if [[ ! -f Makefile ]]; then
      "$src/configure" "${cross[@]}" "${conf[@]}" CFLAGS="$cflags" \
        >>"$log" 2>&1
    fi
    make -j"$JOBS" >>"$log" 2>&1
  )

  local commit
  commit=$(git -C "$src" rev-parse HEAD)
  local inc="-I$bdir -I$src"
  local lib="$bdir/src/.libs/libwolfssl.a"
  if [[ ! -f "$lib" ]]; then
    lib="$bdir/src/libwolfssl.a"
  fi
  if [[ ! -f "$lib" ]]; then
    echo "libwolfssl.a not found for $id" | tee -a "$log"
    return 1
  fi

  local out="$ROOT/harness/probe-$id"
  local cc=gcc
  local link_extra=(-lm -lpthread)
  if [[ "$backend" == neon ]]; then
    cc=aarch64-linux-gnu-gcc
  fi

  echo "[probe] compiling $out" | tee -a "$log"
  "$cc" -O2 $probe_macro $inc \
    -o "$out" "$PROBE_SRC" "$lib" "${link_extra[@]}" \
    >>"$log" 2>&1

  # Persist build metadata
  cat >"$BUILD/$id/build_meta.json" <<EOF
{
  "build_id": "$id",
  "backend": "$backend",
  "source_tree": "$src",
  "resolved_commit": "$commit",
  "configure": "$src/configure ${cross[*]} ${conf[*]} CFLAGS=$cflags",
  "probe_binary": "$out",
  "probe_macro": "$probe_macro",
  "compiler": "$("$cc" --version | head -1)",
  "libwolfssl": "$lib"
}
EOF
  echo "[build] $id OK commit=$commit"
}

cmd="${1:-all-x86}"
case "$cmd" in
  BUILD-PREFIX-SCALAR)  build_one BUILD-PREFIX-SCALAR  "$SRC591" scalar ;;
  BUILD-PREFIX-AVX2)    build_one BUILD-PREFIX-AVX2    "$SRC591" avx2 ;;
  BUILD-POSTFIX-SCALAR) build_one BUILD-POSTFIX-SCALAR "$SRC592" scalar ;;
  BUILD-POSTFIX-AVX2)   build_one BUILD-POSTFIX-AVX2   "$SRC592" avx2 ;;
  BUILD-PREFIX-NEON)    build_one BUILD-PREFIX-NEON    "$SRC591" neon ;;
  BUILD-POSTFIX-NEON)   build_one BUILD-POSTFIX-NEON   "$SRC592" neon ;;
  all-x86)
    build_one BUILD-PREFIX-SCALAR  "$SRC591" scalar &
    p1=$!
    build_one BUILD-PREFIX-AVX2    "$SRC591" avx2 &
    p2=$!
    build_one BUILD-POSTFIX-SCALAR "$SRC592" scalar &
    p3=$!
    build_one BUILD-POSTFIX-AVX2   "$SRC592" avx2 &
    p4=$!
    ec=0
    wait $p1 || ec=1
    wait $p2 || ec=1
    wait $p3 || ec=1
    wait $p4 || ec=1
    exit $ec
    ;;
  all-neon)
    build_one BUILD-PREFIX-NEON  "$SRC591" neon
    build_one BUILD-POSTFIX-NEON "$SRC592" neon
    ;;
  *)
    echo "usage: $0 [BUILD-ID|all-x86|all-neon]" >&2
    exit 2
    ;;
esac
