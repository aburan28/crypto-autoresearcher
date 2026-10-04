#!/usr/bin/env bash
# Run with SQISIGN_UPSTREAM_DIR pointing to a clean, pinned checkout.
# CMake must be installed; this script never downloads code.
set -euo pipefail

probe_dir="$(cd "$(dirname "$0")" && pwd)"
upstream_dir="$SQISIGN_UPSTREAM_DIR"
output_dir="$probe_dir/results"
mkdir -p "$output_dir"

if [[ "$(git -C "$upstream_dir" rev-parse --short=7 HEAD)" != f417ebd ]]; then
    echo "Unexpected upstream commit" >&2
    exit 1
fi
if [[ -n "$(git -C "$upstream_dir" status --porcelain)" ]]; then
    echo "Upstream checkout must be clean before instrumentation" >&2
    exit 1
fi

{
    date -u '+started_utc=%Y-%m-%dT%H:%M:%SZ'
    git -C "$upstream_dir" rev-parse HEAD
    git -C "$upstream_dir" status --short
    git -C "$probe_dir" rev-parse HEAD
    git -C "$probe_dir" status --short
    uname -a
    cc --version | head -1
    cmake --version | head -1
    python3 --version
    sha256sum "$probe_dir"/{protocol.md,timing_probe.c,loop_counter.patch,analyze.py}
} > "$output_dir/metadata.txt"

cmake -S "$upstream_dir" -B "$upstream_dir/build" \
    -DSQISIGN_BUILD_TYPE=ref -DCMAKE_BUILD_TYPE=Release > "$output_dir/configure.log" 2>&1
cmake --build "$upstream_dir/build" --parallel 4 > "$output_dir/build.log" 2>&1
ctest --test-dir "$upstream_dir/build" -R '^sqisign_p324_3_KAT$' \
    --output-on-failure > "$output_dir/kat.log" 2>&1

cp "$probe_dir/timing_probe.c" "$upstream_dir/apps/timing_probe.c"
cat >> "$upstream_dir/apps/CMakeLists.txt" <<'CMAKE'

# Laboratory-only target, never part of the upstream release.
add_executable(timing_probe_p324_3 timing_probe.c)
target_link_libraries(timing_probe_p324_3 PRIVATE sqisign_p324_3_test_nistapi)
target_include_directories(timing_probe_p324_3 PRIVATE ../include ../src/p324_3)
target_compile_definitions(timing_probe_p324_3 PRIVATE SQISIGN_VARIANT=p324_3)
CMAKE

cmake -S "$upstream_dir" -B "$upstream_dir/build" \
    -DSQISIGN_BUILD_TYPE=ref -DCMAKE_BUILD_TYPE=Release >> "$output_dir/configure.log" 2>&1
cmake --build "$upstream_dir/build" --target timing_probe_p324_3 --parallel 4 \
    >> "$output_dir/build.log" 2>&1
"$upstream_dir/build/apps/timing_probe_p324_3" \
    > "$output_dir/pristine.csv" 2> "$output_dir/pristine.stderr"

git -C "$upstream_dir" apply "$probe_dir/loop_counter.patch"
cmake --build "$upstream_dir/build" --target timing_probe_p324_3 --parallel 4 \
    >> "$output_dir/build.log" 2>&1
"$upstream_dir/build/apps/timing_probe_p324_3" \
    > "$output_dir/instrumented.csv" 2> "$output_dir/instrumented.stderr"

python3 "$probe_dir/analyze.py" "$output_dir/pristine.csv" \
    "$output_dir/instrumented.csv" > "$output_dir/analysis.json" \
    2> "$output_dir/analysis.stderr"
date -u '+ended_utc=%Y-%m-%dT%H:%M:%SZ' >> "$output_dir/metadata.txt"
sha256sum "$output_dir"/*.csv "$output_dir/analysis.json" \
    > "$output_dir/result_hashes.txt"
