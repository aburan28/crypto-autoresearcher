#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
#
# Run cppcheck static analysis over the project.
#
#   scripts/cppcheck.sh                     analyze every configuration valid on this host
#   scripts/cppcheck.sh --config=ref,arm64  analyze the named configurations instead
#   scripts/cppcheck.sh --audit             also report suppressions that no longer match anything
#   scripts/cppcheck.sh --github            also emit GitHub workflow-command annotations
#
# Set CPPCHECK=/path/to/cppcheck to choose a specific binary.
#
# This script is the single place the cppcheck flag list appears. `make cppcheck` and the CI
# workflow both invoke it, so a local run and a CI run cannot drift apart in configuration - only in
# cppcheck version, which is deliberately not pinned.
#
# Why one run per configuration: SQISIGN_BUILD_TYPE selects which *directories* get compiled, so a
# single compile_commands.json covers only part of the tree. `ref` compiles src/gf/ref/lvlx, while
# `broadwell`/`arm64` compile src/gf/sat64 instead, each with its own assembly. In CI this pairs up
# as x64 -> ref + broadwell, arm64 -> arm64; the union covers everything.

set -eu

# 2.11 introduced --check-level=exhaustive, which is what makes this analysis worth running; 2.13 is
# the floor because it is what current distributions package and what this was validated against.
MIN_VERSION=2.13

# The exclusions below are repository-relative and qc_exclude_check tests them with -e, so running
# from anywhere else makes every one of them silently stop matching. git prints its own error here.
TOPLEVEL=$(git rev-parse --show-toplevel) || exit 1
cd "$TOPLEVEL"

# QC_EXCLUDE: the vendored and generated code skipped via -i / --suppress below.
. "$TOPLEVEL/scripts/quality_checks_exclusions.sh"

# arm64 and broadwell both compile src/gf/sat64 but each needs its own assembly, so only the one
# matching the host is offered. ref is portable.
case "$(uname -m)" in
    x86_64 | amd64) HOST_CONFIGS="ref broadwell" ;;
    arm64 | aarch64) HOST_CONFIGS="ref arm64" ;;
    *) HOST_CONFIGS="ref" ;;
esac

audit=0
github=0
configs=""

for arg in "$@"; do
    case "$arg" in
        --config=*) configs="$configs ${arg#--config=}" ;;
        --audit) audit=1 ;;
        --github) github=1 ;;
        *)
            echo "error: unknown argument '$arg'; see the comments at the top of $0" >&2
            exit 1
            ;;
    esac
done
IFS=', ' read -ra CONFIGS <<<"${configs:-$HOST_CONFIGS}"

CPPCHECK=${CPPCHECK:-cppcheck}
version=$("$CPPCHECK" --version 2>/dev/null | sed -n 's/^Cppcheck \([0-9][0-9.]*\).*/\1/p') || true
if [ -z "$version" ]; then
    echo "error: cppcheck not found or unrecognised (looked for '$CPPCHECK')." >&2
    echo "       apt-get install cppcheck / brew install cppcheck, or set CPPCHECK=/path/to/it" >&2
    exit 1
fi
if [ "$(printf '%s\n%s\n' "$version" "$MIN_VERSION" | sort -V | head -1)" != "$MIN_VERSION" ]; then
    echo "error: cppcheck $version is too old; this project needs >= $MIN_VERSION." >&2
    echo "       Debian bookworm (2.10) and Ubuntu 22.04 (2.7) are too old: use backports, a newer" >&2
    echo "       release (Debian trixie 2.17, Ubuntu 24.04 2.13), or build from source." >&2
    exit 1
fi

qc_exclude_check "${QC_EXCLUDE[@]}" || exit 1
exclude_args=()
for path in "${QC_EXCLUDE[@]}"; do
    case $path in
        *.h)
            # -i never applies to a header; cppcheck says so and ignores the entry. A file-wide
            # suppression does work.
            exclude_args+=(--suppress="*:$path" --suppress="*:$TOPLEVEL/$path")
            ;;
        *)
            # -i is matched against compile_commands.json, where the path style depends on the CMake
            # version (4.4 writes absolute). Both spellings, so an exclusion cannot silently stop
            # matching.
            exclude_args+=(-i "$path" -i "$TOPLEVEL/$path")
            ;;
    esac
done

# --enable: `error` severity is always on and cannot be disabled; that is where the checks we care
#   about live (bufferAccessOutOfBounds, uninitvar, doubleFree, useAfterFree, nullPointer, ...). The
#   three classes below are additive; `style` is deliberately omitted as noise, and `all` would pull
#   in unusedFunction, which flags every exported symbol of a library.
# --check-level=exhaustive: drops the value-flow cutoffs `normal` applies to complex functions, for
#   about two seconds on this tree.
# --platform=unix64: type sizes feed buffer-size arithmetic; pinning stops results varying by host.
# --relative-paths: needed for GitHub annotations to attach, and keeps output diffable.
# The cert addon is not used (it moved to Cppcheck Premium), nor is misra (out of scope).
CPPCHECK_ARGS=(
    --enable=warning,performance,portability
    --check-level=exhaustive
    --platform=unix64
    --std=c11
    --library=posix
    --inline-suppr
    --template='{file}:{line}:{column}: {severity}: {message} [{id}]'
    --template-location='    {file}:{line}: note: {info}'
    --relative-paths="$TOPLEVEL"
    --error-exitcode=1
    --quiet
    -j "$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)"
    "${exclude_args[@]}"
)

# A suppression that stops matching is a hazard - the finding it hid may have moved rather than gone
# away - but cppcheck says nothing about it by default. --audit turns that into output. It is off by
# default because an inline suppression in a file this configuration does not compile has nothing to
# match against, which is expected rather than wrong. unmatchedSuppression is information-severity,
# so that class has to be enabled; checkersReport comes with it and is a summary, not a finding.
if [ "$audit" -eq 1 ]; then
    CPPCHECK_ARGS+=(--enable=information --suppress=checkersReport)
else
    CPPCHECK_ARGS+=(--suppress=unmatchedSuppression)
fi

echo "cppcheck $version, configurations: ${CONFIGS[*]}"
status=0

for cfg in "${CONFIGS[@]}"; do
    builddir="build-cppcheck-$cfg"
    out="$builddir/findings.txt"

    # A dedicated build directory (build*/ is gitignored), so this never disturbs a developer's own
    # build tree. Only the configure step is needed: cppcheck reads compile_commands.json and never
    # requires compiled objects.
    mkdir -p "$builddir/cache"
    if ! cmake -S . -B "$builddir" -DCMAKE_BUILD_TYPE=Release -DSQISIGN_BUILD_TYPE="$cfg" \
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON >"$builddir/configure.log" 2>&1; then
        echo "error: cmake configure failed for SQISIGN_BUILD_TYPE=$cfg, see $builddir/configure.log" >&2
        exit 1
    fi

    # cppcheck writes findings to stderr and progress to stdout.
    if "$CPPCHECK" --project="$builddir/compile_commands.json" \
        --cppcheck-build-dir="$builddir/cache" "${CPPCHECK_ARGS[@]}" \
        >"$builddir/progress.log" 2>"$out"; then
        echo "$cfg: clean"
        continue
    fi

    status=1
    echo "$cfg:"
    cat "$out"
    if [ "$github" -eq 1 ]; then
        # GitHub accepts only error/warning/notice; an unmapped level would be printed literally
        # instead of becoming an annotation.
        sed -nE 's/^([^ ][^:]*):([0-9]+):([0-9]+): error: /::error file=\1,line=\2,col=\3::/p;
                 s/^([^ ][^:]*):([0-9]+):([0-9]+): warning: /::warning file=\1,line=\2,col=\3::/p;
                 s/^([^ ][^:]*):([0-9]+):([0-9]+): [a-z]+: /::notice file=\1,line=\2,col=\3::/p' "$out"
    fi
done

if [ "$status" -ne 0 ]; then
    cat >&2 <<'EOF'

Fix the defect, or if it is a false positive, annotate the site and say why:

    // cppcheck-suppress <id> ; <why this is not a defect>

The reason is not optional: a suppression without one is indistinguishable from hiding a bug. See
DEVELOPERS.md, "Static analysis", for the false positives already known in this codebase.
EOF
fi
exit "$status"
