#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
#
# Run clang-tidy static analysis over the project.
#
#   scripts/clang-tidy.sh                      analyze every configuration valid on this host
#   scripts/clang-tidy.sh --config=ref,arm64   analyze the named configurations instead
#   scripts/clang-tidy.sh --fix                apply the fixes clang-tidy can make automatically
#   scripts/clang-tidy.sh --github             also emit GitHub workflow-command annotations
#
# Set CLANG_TIDY=/path/to/clang-tidy to pick a specific binary. The check list is in .clang-tidy at the repo root.
# SQISIGN_BUILD_TYPE selects which directories compile; CI runs x64 -> ref + broadwell and arm64 -> arm64.

set -eu

MIN_VERSION=18

# Exclusions and the header filter are matched against repository-relative paths.
TOPLEVEL=$(git rev-parse --show-toplevel) || exit 1
cd "$TOPLEVEL"

# QC_EXCLUDE: the vendored and generated code left out below, as path prefixes.
. "$TOPLEVEL/scripts/quality_checks_exclusions.sh"

# broadwell and arm64 each need their own assembly, so only the one matching the host is offered.
case "$(uname -m)" in
    x86_64 | amd64) HOST_CONFIGS="ref broadwell" ;;
    arm64 | aarch64) HOST_CONFIGS="ref arm64" ;;
    *) HOST_CONFIGS="ref" ;;
esac

fix=0
github=0
configs=""
for arg in "$@"; do
    case "$arg" in
        --config=*) configs="$configs ${arg#--config=}" ;;
        --fix) fix=1 ;;
        --github) github=1 ;;
        *)
            echo "error: unknown argument '$arg'; see the comments at the top of $0" >&2
            exit 1
            ;;
    esac
done
IFS=', ' read -ra CONFIGS <<<"${configs:-$HOST_CONFIGS}"

# First candidate meeting the floor wins. The absolute paths are Homebrew's llvm, which is keg-only.
clang_tidy_version() { "$1" --version 2>/dev/null | sed -n 's/.*LLVM version \([0-9][0-9.]*\).*/\1/p'; }
if [ -n "${CLANG_TIDY:-}" ]; then
    candidates=("$CLANG_TIDY")
else
    candidates=(clang-tidy clang-tidy-22 clang-tidy-21 clang-tidy-20 clang-tidy-19 clang-tidy-18
        /opt/homebrew/opt/llvm/bin/clang-tidy /usr/local/opt/llvm/bin/clang-tidy)
fi
CLANG_TIDY=""
found=""
for cand in "${candidates[@]}"; do
    command -v "$cand" >/dev/null 2>&1 || [ -x "$cand" ] || continue
    version=$(clang_tidy_version "$cand")
    [ -n "$version" ] || continue
    found=${found:-$version}
    if [ "${version%%.*}" -ge "$MIN_VERSION" ]; then
        CLANG_TIDY=$cand
        break
    fi
done
if [ -z "$CLANG_TIDY" ]; then
    if [ -n "$found" ]; then
        echo "error: clang-tidy $found is too old; this project needs >= $MIN_VERSION." >&2
        echo "       Ubuntu 24.04 (18) and Debian 13 (19) are both fine; older releases are not." >&2
    else
        echo "error: clang-tidy not found." >&2
        echo "       apt-get install clang-tidy / brew install llvm, or set CLANG_TIDY=/path/to/it" >&2
    fi
    exit 1
fi
major=${version%%.*}

if ! command -v python3 >/dev/null 2>&1; then
    echo "error: python3 is required to split the compile database by security level." >&2
    exit 1
fi

qc_exclude_check "${QC_EXCLUDE[@]}" || exit 1
exclude_re=$(qc_exclude_regexes "${QC_EXCLUDE[@]}" | paste -sd '|' -)

# --extra-arg comes last so -UNDEBUG beats Release's -DNDEBUG: the analyzer uses the 325 asserts as constraints.
CLANG_TIDY_ARGS=(
    --quiet
    --allow-enabling-analyzer-alpha-checkers  # for clang-analyzer-alpha.security.ArrayBoundV2 on 18 and 19
    --extra-arg=-UNDEBUG
    "--header-filter=^${TOPLEVEL}/(src|include|apps|test)/"
)
# 18 lacks this flag; postprocess() filters the same paths, which is what makes 18 and 19 agree on the output.
if [ "$major" -ge 19 ]; then
    CLANG_TIDY_ARGS+=("--exclude-header-filter=^${TOPLEVEL}/(${exclude_re})")
fi
if [ "$fix" -eq 1 ]; then
    CLANG_TIDY_ARGS+=(--fix --fix-errors)
fi

# --exclude-header-filter does not gate the fix writer, so --fix still rewrites vendored headers. Put them back.
snapshot_excluded() {
    [ "$fix" -eq 1 ] || return 0
    snapdir=$(mktemp -d) || exit 1
    for path in "${QC_EXCLUDE[@]}"; do
        [ -f "$path" ] || continue
        mkdir -p "$snapdir/$(dirname "$path")"
        cp "$path" "$snapdir/$path"
    done
}
restore_excluded() {
    [ "$fix" -eq 1 ] || return 0
    for path in "${QC_EXCLUDE[@]}"; do
        [ -f "$snapdir/$path" ] || continue
        if ! cmp -s "$snapdir/$path" "$path"; then
            cp "$snapdir/$path" "$path"
            echo "note: reverted --fix edits to excluded file $path" >&2
        fi
    done
    rm -rf "$snapdir"
}

# Homebrew's clang-tidy does not inherit the sysroot implicit in the /usr/bin/cc that the database names.
if [ "$(uname -s)" = "Darwin" ] && sdk=$(xcrun --show-sdk-path 2>/dev/null) && [ -n "$sdk" ]; then
    CLANG_TIDY_ARGS+=("--extra-arg=-isysroot$sdk")
fi

# One database per SQISIGN_VARIANT: clang-tidy analyzes a file once per invocation, so a single database would
# cover every lvlx source at one arbitrary security level - and the level sets NWORDS_FIELD. Prints "<variant> <n>".
split_db() {
    python3 - "$TOPLEVEL" "$1" "$2" "$exclude_re" <<'PY'
import collections, json, os, re, sys

top, db_path, outdir, exclude_re = sys.argv[1:5]
skip = re.compile("^(%s)" % exclude_re)
groups = collections.defaultdict(dict)

for entry in json.load(open(db_path)):
    args = entry.get("arguments") or entry.get("command", "").split()
    variant = next((a.split("=", 1)[1] for a in args if a.startswith("-DSQISIGN_VARIANT=")), "generic")
    # One entry per file: sources compiled into both sqisign_<lvl> and sqisign_<lvl>_test repeat verbatim.
    groups[variant].setdefault(entry["file"], entry)

for variant, entries in sorted(groups.items()):
    vdir = os.path.join(outdir, variant)
    os.makedirs(vdir, exist_ok=True)
    with open(os.path.join(vdir, "compile_commands.json"), "w") as f:
        json.dump(list(entries.values()), f)
    # clang-tidy parses whatever the database lists as C, so assembly would be a clang-diagnostic-error.
    files = [
        rel
        for rel in (os.path.relpath(p, top) for p in entries)
        if not rel.endswith((".S", ".s", ".asm")) and not skip.match(rel)
    ]
    with open(os.path.join(vdir, "files.txt"), "w") as f:
        f.writelines(rel + "\n" for rel in files)
    print(variant, len(files))
PY
}

# Repo-relative paths, then drop whole diagnostics that land in vendored code or repeat one already printed.
# Keyed on location plus check and not on the message: namespacing repeats one lvlx finding once per level.
postprocess() {
    sed -e "s|${TOPLEVEL}/||g" -e ':a' -e 's|[^/ ]*/\.\./||' -e 'ta' | awk -v excl="$exclude_re" '
        /^[^[:space:]].*: (warning|error): / {
            path = $0; sub(/:.*$/, "", path)
            loc = $0; sub(/: (warning|error): .*$/, "", loc)
            chk = ""
            if (match($0, /\[[A-Za-z0-9.,_-]+\]$/)) chk = substr($0, RSTART, RLENGTH)
            key = loc "|" chk
            drop = (path ~ ("^(" excl ")")) || (key in seen)
            seen[key] = 1
        }
        !drop { print }
    '
}

# --fix must not run concurrently: two translation units including the same header would race to rewrite it.
if [ "$fix" -eq 1 ]; then
    jobs=1
else
    jobs=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)
fi

echo "clang-tidy $version, configurations: ${CONFIGS[*]}"
status=0
snapshot_excluded
trap restore_excluded EXIT

for cfg in "${CONFIGS[@]}"; do
    builddir="build-clang-tidy-$cfg"
    out="$builddir/findings.txt"
    raw="$builddir/raw.txt"

    # Dedicated build directory (build*/ is gitignored); only configure is needed, never the objects.
    mkdir -p "$builddir"
    if ! cmake -S . -B "$builddir" -DCMAKE_BUILD_TYPE=Release -DSQISIGN_BUILD_TYPE="$cfg" \
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON >"$builddir/configure.log" 2>&1; then
        echo "error: cmake configure failed for SQISIGN_BUILD_TYPE=$cfg, see $builddir/configure.log" >&2
        exit 1
    fi

    : >"$raw"
    : >"$builddir/stderr.log"
    split_db "$builddir/compile_commands.json" "$builddir/db" >"$builddir/splits.txt"

    analyzed=0
    while read -r variant count; do
        analyzed=$((analyzed + count))
        [ "$count" -gt 0 ] || continue
        xargs -P "$jobs" -I{} "$CLANG_TIDY" -p "$builddir/db/$variant" "${CLANG_TIDY_ARGS[@]}" {} \
            <"$builddir/db/$variant/files.txt" >>"$raw" 2>>"$builddir/stderr.log" || true
    done <"$builddir/splits.txt"
    postprocess <"$raw" >"$out"

    # A run that analyzed nothing reports "clean" just as loudly as one that analyzed everything.
    if [ "$analyzed" -eq 0 ]; then
        echo "error: $cfg: no translation units were analyzed. This is a bug in $0, not a clean tree." >&2
        exit 1
    fi

    if [ ! -s "$out" ]; then
        echo "$cfg: clean ($analyzed translation units)"
        continue
    fi

    status=1
    echo "$cfg:"
    cat "$out"
    if [ "$github" -eq 1 ]; then
        # GitHub accepts only error/warning/notice; an unmapped level is printed literally instead of annotating.
        sed -nE 's/^([^ ][^:]*):([0-9]+):([0-9]+): error: /::error file=\1,line=\2,col=\3::/p;
                 s/^([^ ][^:]*):([0-9]+):([0-9]+): warning: /::warning file=\1,line=\2,col=\3::/p' "$out"
    fi
done

if [ "$status" -ne 0 ]; then
    cat >&2 <<'EOF'

Fix the defect, or if it is a false positive, annotate the site and say why:

    // NOLINTNEXTLINE(<check>) - <why this is not a defect>

Name the specific check and give the reason - never a bare NOLINT. See DEVELOPERS.md, "Static analysis".
EOF
fi
exit "$status"
